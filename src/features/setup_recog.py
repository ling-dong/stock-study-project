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
    def __init__(self, volume_shrink_ratio: float = 0.8,
                 breakout_volume_multiplier: float = 1.2,
                 breakout_body_ratio: float = 0.5,
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
        """处理新Bar，检测候选/确认Setup"""
        self._history.append(bar)
        self._bar_counter += 1
        if len(self._history) > 100:
            self._history = self._history[-100:]

        if len(self._history) < 10:
            return None

        # 检测H2候选
        h2_candidate = self._detect_h2_candidate()
        if h2_candidate:
            self._candidates[("H2", self._bar_counter)] = h2_candidate
            return SetupSignal(
                symbol=bar.symbol, timestamp=bar.timestamp,
                setup_type=SetupType.H2,
                candidate_vs_confirmed=SetupStatus.CANDIDATE,
                quality_score=h2_candidate["quality"],
                maturity=0,
                detection_bar_index=self._bar_counter,
            )

        # 检测H2确认
        for key, candidate in list(self._candidates.items()):
            if key[0] == "H2":
                confirmed = self._check_h2_confirmation(candidate)
                if confirmed:
                    del self._candidates[key]
                    return SetupSignal(
                        symbol=bar.symbol, timestamp=bar.timestamp,
                        setup_type=SetupType.H2,
                        candidate_vs_confirmed=SetupStatus.CONFIRMED,
                        quality_score=confirmed,
                        maturity=self._bar_counter - key[1],
                        detection_bar_index=self._bar_counter,
                    )

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

    def _calc_quality(self, pullback_sim: float, vol_ratio: float,
                      breakout_momentum: float) -> float:
        return self.w1 * pullback_sim + self.w2 * (1.0 - vol_ratio) + self.w3 * breakout_momentum
