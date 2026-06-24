"""§4.2.2 MarketStateSvc — 市场状态机

有状态服务，基于EMA20斜率+趋势K线比例+ADX判定三态(bull/bear/neutral)。
延迟确认机制：需连续2根Bar满足条件才切换状态——消除前视偏差与噪声干扰。
"""
from datetime import datetime
from typing import List, Optional, Tuple
import numpy as np
from src.models.bar import BarOHLCV
from src.models.market_state import MarketState, MarketStateType, RegimeType
from src.features.bar_feature import BarFeatureSvc


class MarketStateSvc:
    """市场状态机 — §4.2.2

    特性:
    - 有状态: 维护当前状态、持续时间和历史K线上下文
    - 延迟确认: 需连续2根Bar确认才切换状态
    - 延迟预算: <500ms
    - 降级策略: 状态不确定时输出NEUTRAL
    """

    def __init__(self, ema_period: int = 20, adx_period: int = 14,
                 adx_threshold: int = 25, trend_ratio_bull: float = 0.6,
                 trend_ratio_bear: float = 0.4, confirmation_bars: int = 2,
                 initial_confidence: float = 0.3, confidence_per_bar: float = 0.05,
                 max_confidence: float = 0.9):
        self.ema_period = ema_period
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.trend_ratio_bull = trend_ratio_bull
        self.trend_ratio_bear = trend_ratio_bear
        self.confirmation_bars = confirmation_bars
        self.initial_confidence = initial_confidence
        self.confidence_per_bar = confidence_per_bar
        self.max_confidence = max_confidence

        self._bar_feature = BarFeatureSvc()
        self._current_state: Optional[MarketStateType] = None
        self._pending_state: Optional[MarketStateType] = None
        self._pending_count: int = 0
        self._duration: int = 0
        self._history_bars: List[BarOHLCV] = []

    def update(self, bar: BarOHLCV) -> Optional[MarketState]:
        """处理新Bar，输出可能的状态变更

        Args:
            bar: 新闭合的BarOHLCV

        Returns:
            MarketState(状态变更时) 或 None(状态未变更)
        """
        self._history_bars.append(bar)
        if len(self._history_bars) > max(self.ema_period, self.adx_period) * 3:
            self._history_bars = self._history_bars[-max(self.ema_period, self.adx_period) * 3:]

        if len(self._history_bars) < self.ema_period + 1:
            return None

        # 计算EMA20斜率
        closes = np.array([float(b.close) for b in self._history_bars])
        ema20 = self._calc_ema(closes, self.ema_period)
        ema_slope = ema20[-1] - ema20[-2]

        # 计算趋势K线比例
        recent_bars = self._history_bars[-20:]
        trend_count = sum(1 for b in recent_bars if self._bar_feature.compute_body_ratio(b) > 0.5 and float(b.close) > float(b.open))
        trend_ratio = trend_count / len(recent_bars) if recent_bars else 0.5

        # 计算ADX(14)
        adx_value = self._calc_adx(self._history_bars, self.adx_period)

        # 判定状态
        if ema_slope > 0 and trend_ratio > self.trend_ratio_bull and adx_value > self.adx_threshold:
            new_state = MarketStateType.BULL
        elif ema_slope < 0 and trend_ratio < self.trend_ratio_bear and adx_value > self.adx_threshold:
            new_state = MarketStateType.BEAR
        else:
            new_state = MarketStateType.NEUTRAL

        # 延迟确认机制
        if new_state == self._pending_state:
            self._pending_count += 1
        else:
            self._pending_state = new_state
            self._pending_count = 1

        if self._pending_count >= self.confirmation_bars:
            if new_state != self._current_state or self._current_state is None:
                self._current_state = new_state
                self._duration = 1
                return self._build_state(bar)
            else:
                self._duration += 1
                return self._build_state(bar)

        # 状态未确认，若当前无状态则返回NEUTRAL
        if self._current_state is None:
            self._current_state = MarketStateType.NEUTRAL
            self._duration = 1
            return self._build_state(bar)

        self._duration += 1
        return None  # 状态未变更

    def _build_state(self, bar: BarOHLCV) -> MarketState:
        from decimal import Decimal
        confidence = min(
            self.initial_confidence + self._duration * self.confidence_per_bar,
            self.max_confidence
        )
        # regime分类
        adx = self._calc_adx(self._history_bars, self.adx_period) if len(self._history_bars) >= self.adx_period + 1 else 0
        if adx > 25:
            regime = RegimeType.TRENDING
        elif adx > 15:
            regime = RegimeType.VOLATILE
        else:
            regime = RegimeType.RANGING

        return MarketState(
            symbol=bar.symbol,
            timestamp=bar.timestamp,
            timeframe=bar.timeframe.value,
            state=self._current_state,
            confidence=Decimal(str(round(confidence, 3))),
            duration=self._duration,
            regime_classification=regime,
        )

    def get_current_state(self) -> Optional[MarketStateType]:
        return self._current_state

    def _calc_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        alpha = 2.0 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
        return ema

    def _calc_adx(self, bars: List[BarOHLCV], period: int = 14) -> float:
        """计算ADX(平均趋向指数)"""
        if len(bars) < period + 1:
            return 0.0
        highs = np.array([float(b.high) for b in bars])
        lows = np.array([float(b.low) for b in bars])
        closes = np.array([float(b.close) for b in bars])

        tr = np.zeros(len(bars))
        plus_dm = np.zeros(len(bars))
        minus_dm = np.zeros(len(bars))

        for i in range(1, len(bars)):
            tr[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            plus_dm[i] = up_move if up_move > down_move and up_move > 0 else 0
            minus_dm[i] = down_move if down_move > up_move and down_move > 0 else 0

        atr = self._calc_wilder_smooth(tr, period)
        plus_di = self._calc_wilder_smooth(plus_dm, period) / (atr + 1e-10) * 100
        minus_di = self._calc_wilder_smooth(minus_dm, period) / (atr + 1e-10) * 100

        dx = abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) * 100
        adx = np.zeros_like(dx)
        for i in range(period, len(dx)):
            if i == period:
                adx[i] = np.mean(dx[1:period+1])
            else:
                adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period

        return float(adx[-1]) if len(adx) > 0 else 0.0

    def _calc_wilder_smooth(self, data: np.ndarray, period: int) -> np.ndarray:
        result = np.zeros_like(data)
        result[period] = np.mean(data[1:period+1])
        for i in range(period + 1, len(data)):
            result[i] = (result[i-1] * (period - 1) + data[i]) / period
        return result
