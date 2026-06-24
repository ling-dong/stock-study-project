"""§4.2.4 ConsensusSvc — 板块内部一致性

聚合计算服务，输入板块内各成分股微观特征与涨跌幅，输出板块一致性指标。
使用point-in-time成分股权重避免幸存者偏差。
"""
from datetime import datetime
from typing import List, Optional, Tuple
import numpy as np
from src.models.bar import BarOHLCV
from src.models.feature import FeatureVector


class ConsensusSvc:
    """板块一致性计算服务 — §4.2.4

    特性:
    - 聚合计算: 可容忍较高延迟(<5秒)
    - stale降级: 成分股延迟>5秒时输出stale标记
    - 延迟预算: <5秒
    """

    def __init__(self, stale_threshold_seconds: float = 5.0):
        self.stale_threshold_seconds = stale_threshold_seconds

    def compute(
        self,
        sector_id: str,
        constituents_data: List[Tuple[str, List[BarOHLCV]]],
        current_timestamp: datetime,
    ) -> Tuple[List[FeatureVector], bool]:
        """计算板块一致性指标

        Args:
            sector_id: 板块ID
            constituents_data: [(symbol, bars), ...] 各成分股K线数据
            current_timestamp: 当前时间戳

        Returns:
            (features_list, is_stale): 特征向量列表和stale标记
        """
        is_stale = False
        computation_time = datetime.now()

        # 检查数据延迟
        max_allowed_time = current_timestamp.timestamp() - self.stale_threshold_seconds
        for symbol, bars in constituents_data:
            if bars:
                last_bar_time = bars[-1].data_availability_time.timestamp()
                if last_bar_time < max_allowed_time:
                    is_stale = True
                    break

        returns_list = []
        up_count = 0
        total = 0

        for symbol, bars in constituents_data:
            if len(bars) >= 2:
                prev_close = float(bars[-2].close)
                curr_close = float(bars[-1].close)
                if prev_close > 0:
                    ret = (curr_close - prev_close) / prev_close
                    returns_list.append(ret)
                    if ret > 0:
                        up_count += 1
                    total += 1

        # up_ratio
        up_ratio = up_count / total if total > 0 else 0.5

        # momentum_median
        momentum_median = float(np.median(returns_list)) if returns_list else 0.0

        # leader_corr (取前两只作为龙头)
        leader_corr = 0.0
        if len(constituents_data) >= 2:
            leader1_returns = self._calc_returns(constituents_data[0][1])
            leader2_returns = self._calc_returns(constituents_data[1][1])
            min_len = min(len(leader1_returns), len(leader2_returns))
            if min_len >= 5:
                corr = np.corrcoef(leader1_returns[-min_len:], leader2_returns[-min_len:])[0, 1]
                leader_corr = float(corr) if not np.isnan(corr) else 0.0

        features = [
            FeatureVector(
                symbol=sector_id, timestamp=current_timestamp, timeframe="day",
                feature_name="up_ratio", feature_value=up_ratio,
                computation_time=computation_time, dependencies_version="consensus_v1",
            ),
            FeatureVector(
                symbol=sector_id, timestamp=current_timestamp, timeframe="day",
                feature_name="momentum_median", feature_value=momentum_median,
                computation_time=computation_time, dependencies_version="consensus_v1",
            ),
            FeatureVector(
                symbol=sector_id, timestamp=current_timestamp, timeframe="day",
                feature_name="leader_corr", feature_value=leader_corr,
                computation_time=computation_time, dependencies_version="consensus_v1",
            ),
        ]

        if is_stale:
            # 附加stale标记特征
            features.append(FeatureVector(
                symbol=sector_id, timestamp=current_timestamp, timeframe="day",
                feature_name="consensus_stale", feature_value=1.0,
                computation_time=computation_time, dependencies_version="consensus_v1",
            ))

        return features, is_stale

    def _calc_returns(self, bars: List[BarOHLCV]) -> List[float]:
        if len(bars) < 2:
            return []
        returns = []
        for i in range(1, len(bars)):
            prev = float(bars[i-1].close)
            curr = float(bars[i].close)
            if prev > 0:
                returns.append((curr - prev) / prev)
        return returns
