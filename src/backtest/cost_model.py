"""§4.6.2 完整交易成本模型"""
from typing import Tuple


class CostModel:
    """交易成本模型 — §4.6.2, §6.1.3"""

    def __init__(self, commission_bps: float = 0.25, stamp_duty_bps: float = 1.0,
                 slippage_min_bps: float = 0.5, slippage_max_bps: float = 1.5):
        self.commission_bps = commission_bps
        self.stamp_duty_bps = stamp_duty_bps
        self.slippage_min_bps = slippage_min_bps
        self.slippage_max_bps = slippage_max_bps

    def round_trip_cost(self, price: float, volume_pct: float = 0.05) -> float:
        """往返交易成本"""
        commission = price * (self.commission_bps / 10000) * 2  # 双向
        stamp = price * (self.stamp_duty_bps / 10000)  # 卖出单边
        slippage = price * (self.slippage_min_bps / 10000)  # 保守估计
        return commission + stamp + slippage

    def expected_value(self, win_prob: float, lose_prob: float, flat_prob: float,
                       target_return: float, stop_loss: float,
                       price: float = 3.5) -> float:
        """三态期望收益 — §6.1.3"""
        cost = self.round_trip_cost(price)
        win_term = win_prob * (target_return - cost)
        lose_term = lose_prob * (abs(stop_loss) + cost)
        flat_term = flat_prob * 0.0  # flat时约等于0
        return win_term - lose_term + flat_term
