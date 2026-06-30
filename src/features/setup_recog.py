"""§4.2.3 SetupRecogSvc — Setup识别(H2/L2/FB)

规则引擎型微服务，识别Wyckoff交易框架关键结构形态。
候选态(candidate)→确认态(confirmed)状态机，区分两者以消除数据泄漏。
"""
from datetime import datetime
from typing import List, Optional, Tuple
import numpy as np
from src.models.bar import BarOHLCV
from src.models.setup_signal import SetupSignal, SetupType, SetupStatus
from src.features.bar_feature import BarFeatureSvc


class SetupRecogSvc:
    def __init__(self, volume_shrink_ratio: float = 0.92,
                 breakout_volume_multiplier: float = 1.05,
                 breakout_body_ratio: float = 0.30,
                 pullback_sim_weight: float = 0.35,
                 volume_shrink_weight: float = 0.30,
                 breakout_momentum_weight: float = 0.35):
        self.volume_shrink_ratio = volume_shrink_ratio
        self.breakout_volume_multiplier = breakout_volume_multiplier
        self.breakout_body_ratio = breakout_body_ratio
        self.w1 = pullback_sim_weight
        self.w2 = volume_shrink_weight
        self.w3 = breakout_momentum_weight
        self._bar_feature = BarFeatureSvc()
        self._history: List[BarOHLCV] = []
        self._candidates: dict = {}  # (type, start_idx) -> candidate info
        self._bar_counter: int = 0
        self._last_detected_leg2_idx: Optional[int] = None

    def update(self, bar: BarOHLCV) -> Optional[SetupSignal]:
        """处理新Bar，检测候选/确认Setup (H2 + L2)"""
        self._history.append(bar)
        self._bar_counter += 1
        if len(self._history) > 100:
            self._history = self._history[-100:]

        if len(self._history) < 15:
            return None

        # ---- H2 检测 (上涨趋势中的两腿回撤) ----
        h2_result = self._detect_h2_candidate()
        if h2_result:
            self._candidates[("H2", self._bar_counter)] = h2_result
            return SetupSignal(
                symbol=bar.symbol, timestamp=bar.timestamp,
                setup_type=SetupType.H2,
                candidate_vs_confirmed=SetupStatus.CANDIDATE,
                quality_score=h2_result["quality"],
                maturity=0, detection_bar_index=self._bar_counter,
            )

        # ---- L2 检测 (下跌趋势中的两腿反弹) ----
        l2_result = self._detect_l2_candidate()
        if l2_result:
            self._candidates[("L2", self._bar_counter)] = l2_result
            return SetupSignal(
                symbol=bar.symbol, timestamp=bar.timestamp,
                setup_type=SetupType.L2,
                candidate_vs_confirmed=SetupStatus.CANDIDATE,
                quality_score=l2_result["quality"],
                maturity=0, detection_bar_index=self._bar_counter,
            )

        # ---- 确认检查 (H2 + L2) ----
        for key, candidate in list(self._candidates.items()):
            setup_type_str, _ = key
            if setup_type_str == "H2":
                confirmed = self._check_h2_confirmation(candidate)
            elif setup_type_str == "L2":
                confirmed = self._check_l2_confirmation(candidate)
            else:
                continue

            if confirmed is not None:
                del self._candidates[key]
                return SetupSignal(
                    symbol=bar.symbol, timestamp=bar.timestamp,
                    setup_type=SetupType(setup_type_str),
                    candidate_vs_confirmed=SetupStatus.CONFIRMED,
                    quality_score=confirmed,
                    maturity=self._bar_counter - key[1],
                    detection_bar_index=self._bar_counter,
                )

        # ---- 候选过期清理 ----
        expired = [
            k for k, v in self._candidates.items()
            if self._bar_counter - k[1] > 30  # 30根Bar未确认 → 失效
        ]
        for k in expired:
            del self._candidates[k]

        return None

    def _detect_h2_candidate(self) -> Optional[dict]:
        """检测H2结构候选态

        条件:
        1. 最近有上升趋势(前5-15根Bar)
        2. 形成两腿回撤结构
        3. 第二腿成交量萎缩
        """
        if len(self._history) < 15:
            return None

        closes = np.array([float(b.close) for b in self._history])
        volumes = np.array([float(b.volume) for b in self._history])

        # 寻找两个回撤低点(简化版)
        n = len(closes)
        # 找局部低点
        lows = []
        for i in range(2, n - 2):
            if closes[i] < closes[i-1] and closes[i] < closes[i-2] and closes[i] < closes[i+1] and closes[i] < closes[i+2]:
                lows.append(i)

        if len(lows) < 2:
            return None

        # 最近两个低点
        leg1_idx = lows[-2]
        leg2_idx = lows[-1]

        # 防止重复检测同一腿结构
        if self._last_detected_leg2_idx is not None and leg2_idx <= self._last_detected_leg2_idx:
            return None

        # 第二腿应比第一腿高(上涨趋势中的higher low)
        if closes[leg2_idx] <= closes[leg1_idx]:
            return None

        # 成交量萎缩检查
        vol_leg1 = np.mean(volumes[leg1_idx-2:leg1_idx+3])
        vol_leg2 = np.mean(volumes[leg2_idx-2:leg2_idx+3])
        if vol_leg1 == 0:
            return None
        vol_ratio = vol_leg2 / vol_leg1

        if vol_ratio >= self.volume_shrink_ratio:
            return None

        # 两腿回撤比例相似度
        pivot_high = max(closes[leg1_idx:leg2_idx+1])
        leg1_depth = pivot_high - closes[leg1_idx]
        leg2_depth = pivot_high - closes[leg2_idx]
        if leg1_depth <= 0:
            return None
        depth_ratio = leg2_depth / leg1_depth
        pullback_sim = max(0.0, 1.0 - abs(1.0 - depth_ratio))

        quality = self._calc_quality(pullback_sim, vol_ratio, 0.0)

        self._last_detected_leg2_idx = leg2_idx

        return {
            "quality": round(min(1.0, quality), 3),
            "pivot_high": float(pivot_high),
            "leg2_idx": leg2_idx,
            "vol_ratio": float(vol_ratio),
        }

    def _check_h2_confirmation(self, candidate: dict) -> Optional[float]:
        """检查H2确认条件

        条件:
        1. 价格向上突破H2结构极点
        2. 成交量放大(>前5根均值*1.2)
        3. 突破Bar实体比例>0.5
        """
        current = self._history[-1]
        pivot = candidate["pivot_high"]
        c, o = float(current.close), float(current.open)

        if c <= pivot and o <= pivot:
            return None

        recent_vols = [float(b.volume) for b in self._history[-6:-1]]
        avg_vol = np.mean(recent_vols) if recent_vols else float(current.volume)
        if float(current.volume) < avg_vol * self.breakout_volume_multiplier:
            return None

        body_ratio = self._bar_feature.compute_body_ratio(current)
        if body_ratio < self.breakout_body_ratio:
            return None

        breakout_momentum = body_ratio
        quality = self._calc_quality(
            1.0, candidate["vol_ratio"], breakout_momentum
        )
        return round(min(1.0, quality), 3)

    # ================================================================
    # L2 Setup — 下跌趋势中的两腿反弹 (lower high)
    # ================================================================
    def _detect_l2_candidate(self) -> Optional[dict]:
        """检测L2结构候选态

        条件 (H2的镜像):
        1. 最近有下跌趋势 — EMA20斜率为负
        2. 形成两腿反弹结构 (lower high)
        3. 第二腿成交量萎缩
        """
        if len(self._history) < 15:
            return None

        closes = np.array([float(b.close) for b in self._history])
        volumes = np.array([float(b.volume) for b in self._history])

        # 趋势过滤: EMA斜率负 + 价格在MA下方 + ADX确认趋势强度
        if len(closes) >= 22:
            alpha = 2.0 / 21.0
            ema = np.zeros_like(closes)
            ema[0] = closes[0]
            for i in range(1, len(closes)):
                ema[i] = alpha * closes[i] + (1.0 - alpha) * ema[i-1]
            ema_declining = ema[-1] < ema[-5]
            price_below_ema = closes[-1] < ema[-1]

            # ADX(14)趋势强度 — 与MarketStateSvc保持一致
            adx = self._calc_adx()
            trend_strong = adx >= 18  # 日线校准阈值

            if not (ema_declining and price_below_ema and trend_strong):
                return None

        n = len(closes)
        highs = []
        for i in range(2, n - 2):
            if closes[i] > closes[i-1] and closes[i] > closes[i-2] \
               and closes[i] > closes[i+1] and closes[i] > closes[i+2]:
                highs.append(i)

        if len(highs) < 2:
            return None

        leg1_idx = highs[-2]
        leg2_idx = highs[-1]

        # 第二腿应比第一腿低 (下跌趋势中的 lower high)
        if closes[leg2_idx] >= closes[leg1_idx]:
            return None

        # 成交量萎缩检查
        if leg1_idx < 2 or leg2_idx < 2:
            return None
        vol_leg1 = np.mean(volumes[leg1_idx-2:leg1_idx+3])
        vol_leg2 = np.mean(volumes[leg2_idx-2:leg2_idx+3])
        if vol_leg1 == 0:
            return None
        vol_ratio = vol_leg2 / vol_leg1

        if vol_ratio >= self.volume_shrink_ratio:
            return None

        # 两腿反弹幅度相似度
        pivot_low = min(closes[leg1_idx:leg2_idx+1])
        leg1_height = closes[leg1_idx] - pivot_low
        leg2_height = closes[leg2_idx] - pivot_low
        if leg1_height <= 0:
            return None
        height_ratio = leg2_height / leg1_height
        pullback_sim = max(0.0, 1.0 - abs(1.0 - height_ratio))

        quality = self._calc_quality(pullback_sim, vol_ratio, 0.0)

        return {
            "quality": round(min(1.0, quality), 3),
            "pivot_low": float(pivot_low),
            "leg2_idx": leg2_idx,
            "vol_ratio": float(vol_ratio),
        }

    def _check_l2_confirmation(self, candidate: dict) -> Optional[float]:
        """检查L2确认条件 (H2的镜像)

        条件:
        1. 价格向下跌破L2结构低点
        2. 成交量放大 (>前5根均值×1.2)
        3. 突破Bar实体比例>threshold
        """
        current = self._history[-1]
        pivot = candidate["pivot_low"]
        c, o = float(current.close), float(current.open)

        # 向下突破 (mirror: 向上突破)
        if c >= pivot and o >= pivot:
            return None

        recent_vols = [float(b.volume) for b in self._history[-6:-1]]
        avg_vol = np.mean(recent_vols) if recent_vols else float(current.volume)
        if float(current.volume) < avg_vol * self.breakout_volume_multiplier:
            return None

        body_ratio = self._bar_feature.compute_body_ratio(current)
        if body_ratio < self.breakout_body_ratio:
            return None

        breakout_momentum = body_ratio
        quality = self._calc_quality(
            1.0, candidate["vol_ratio"], breakout_momentum
        )
        return round(min(1.0, quality), 3)

    def _calc_adx(self, period: int = 14) -> float:
        """计算ADX趋势强度 (复用MarketStateSvc逻辑)"""
        if len(self._history) < period + 1:
            return 0.0
        highs = np.array([float(b.high) for b in self._history])
        lows = np.array([float(b.low) for b in self._history])
        closes_arr = np.array([float(b.close) for b in self._history])

        tr = np.zeros(len(self._history))
        plus_dm = np.zeros(len(self._history))
        minus_dm = np.zeros(len(self._history))

        for i in range(1, len(self._history)):
            tr[i] = max(highs[i] - lows[i],
                        abs(highs[i] - closes_arr[i-1]),
                        abs(lows[i] - closes_arr[i-1]))
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            plus_dm[i] = up_move if up_move > down_move and up_move > 0 else 0
            minus_dm[i] = down_move if down_move > up_move and down_move > 0 else 0

        atr = self._wilder_smooth(tr, period)
        plus_di = self._wilder_smooth(plus_dm, period) / (atr + 1e-10) * 100
        minus_di = self._wilder_smooth(minus_dm, period) / (atr + 1e-10) * 100

        dx = abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) * 100
        adx = np.zeros_like(dx)
        for i in range(period, len(dx)):
            if i == period:
                adx[i] = np.mean(dx[1:period+1])
            else:
                adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period

        return float(adx[-1]) if len(adx) > 0 else 0.0

    def _wilder_smooth(self, data: np.ndarray, period: int) -> np.ndarray:
        result = np.zeros_like(data)
        result[period] = np.mean(data[1:period+1])
        for i in range(period + 1, len(data)):
            result[i] = (result[i-1] * (period - 1) + data[i]) / period
        return result

    def _calc_quality(self, pullback_sim: float, vol_ratio: float,
                      breakout_momentum: float) -> float:
        return self.w1 * pullback_sim + self.w2 * (1.0 - vol_ratio) + self.w3 * breakout_momentum
