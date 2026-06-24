"""§4.2.1 BarFeatureSvc — K线微观结构特征

无状态纯计算微服务。输入标准化BarOHLCV，输出6维微观结构特征向量。
所有特征基于lagged价格计算，禁止引入未来信息。
"""
from datetime import datetime
from typing import List
import numpy as np
from src.models.bar import BarOHLCV
from src.models.feature import FeatureVector

EPSILON = 1e-10


class BarFeatureSvc:
    """K线微观结构特征计算服务 — §4.2.1

    特性:
    - 无状态: 每次compute独立运算，支持水平扩展
    - 延迟预算: <1秒
    - 涨跌停标记作为独立布尔特征输出，用于下游Setup识别突破有效性筛选
    """

    def compute(self, bars: List[BarOHLCV]) -> List[FeatureVector]:
        """计算单根或多根Bar的微观结构特征向量

        Args:
            bars: BarOHLCV列表

        Returns:
            FeatureVector列表，每个Bar对应6个特征(共6*N条特征向量)
        """
        features = []
        computation_time = datetime.now()
        for bar in bars:
            features.extend(self._compute_single(bar, computation_time))
        return features

    def _compute_single(self, bar: BarOHLCV, computation_time: datetime) -> List[FeatureVector]:
        """计算单根Bar的6维微观特征"""
        o = float(bar.open)
        h = float(bar.high)
        l = float(bar.low)
        c = float(bar.close)
        hl_range = h - l + EPSILON

        # 实体比例
        body_ratio = abs(c - o) / hl_range
        # 收盘价位置
        close_position = (c - l) / hl_range
        # 上影线比例
        upper_shadow = (h - max(o, c)) / hl_range
        # 下影线比例
        lower_shadow = (min(o, c) - l) / hl_range
        # 趋势K线标识: 1=阳线, -1=阴线, 0=十字星
        if c > o:
            trend_bar = 1
        elif c < o:
            trend_bar = -1
        else:
            trend_bar = 0
        # 涨跌停标记: 1=涨停, -1=跌停, 0=正常
        limit_status = self._detect_limit(bar)

        # 构建前5个float特征
        base_features = {
            "body_ratio": body_ratio,
            "close_position": close_position,
            "upper_shadow": upper_shadow,
            "lower_shadow": lower_shadow,
            "trend_bar": float(trend_bar),
        }

        deps_version = f"bar_v{bar.data_version}"
        result = []
        for fname, fval in base_features.items():
            result.append(FeatureVector(
                symbol=bar.symbol,
                timestamp=bar.timestamp,
                timeframe=bar.timeframe.value,
                feature_name=fname,
                feature_value=fval,
                computation_time=computation_time,
                dependencies_version=deps_version,
            ))

        # 涨跌停标记作为独立特征
        result.append(FeatureVector(
            symbol=bar.symbol,
            timestamp=bar.timestamp,
            timeframe=bar.timeframe.value,
            feature_name="limit_status",
            feature_value=float(limit_status),
            computation_time=computation_time,
            dependencies_version=deps_version,
        ))

        return result

    def _detect_limit(self, bar: BarOHLCV) -> int:
        """检测涨跌停状态

        注意: 精确涨跌停检测需知道标的前收盘价和板块涨跌幅限制。
        此处为简化实现，基于Bar内价格行为做近似判断:
        - 实体比例极小(>0.95)且high==low → 涨跌停
        """
        o, h, l, c = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
        hl_range = h - l
        if hl_range < EPSILON:
            return 0  # 无交易，无法判断

        body_ratio = abs(c - o) / (hl_range + EPSILON)
        # 涨停特征: 大阳线+收盘接近最高价
        if body_ratio > 0.95 and (h - c) / (hl_range + EPSILON) < 0.05 and c > o:
            return 1
        # 跌停特征: 大阴线+收盘接近最低价
        if body_ratio > 0.95 and (c - l) / (hl_range + EPSILON) < 0.05 and c < o:
            return -1
        return 0

    def compute_body_ratio(self, bar: BarOHLCV) -> float:
        """便捷方法: 计算单根Bar实体比例"""
        return abs(float(bar.close) - float(bar.open)) / (float(bar.high) - float(bar.low) + EPSILON)

    def compute_close_position(self, bar: BarOHLCV) -> float:
        """便捷方法: 计算收盘价相对位置"""
        return (float(bar.close) - float(bar.low)) / (float(bar.high) - float(bar.low) + EPSILON)

    def is_trend_bar(self, bar: BarOHLCV) -> bool:
        """判断是否为趋势K线(实体比例>50%)"""
        return self.compute_body_ratio(bar) > 0.5
