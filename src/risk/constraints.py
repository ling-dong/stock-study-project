"""§6.1.3 六层硬约束体系 + 凯利公式

约束优先级: L4 > L3 > L2 > L1 > L5 > L6
"""
from typing import Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PortfolioState:
    """投资组合状态"""
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    monthly_pnl: float = 0.0
    max_drawdown: float = 0.0
    total_exposure: float = 0.0
    sector_exposures: dict = field(default_factory=dict)
    consecutive_losses: int = 0
    total_trades_today: int = 0


class RiskConstraints:
    """六层硬约束 — §6.1.3 表"""

    def __init__(self):
        self.L1_daily = -0.03
        self.L2_weekly = -0.08
        self.L3_monthly = -0.15
        self.L4_max_dd = -0.20
        self.L5_sector = 0.20
        self.L6_total = 0.80

    def evaluate(self, symbol: str, proposed_position: float, state: PortfolioState) -> Tuple[bool, str, float]:
        """评估风控闸门

        Returns: (allowed, reason, adjusted_position)
        """
        # L4 最高优先级
        if state.max_drawdown <= self.L4_max_dd:
            return False, f"L4: 最大回撤{state.max_drawdown:.1%}超{abs(self.L4_max_dd):.0%}", 0.0
        # L3
        if state.monthly_pnl <= self.L3_monthly:
            return False, f"L3: 月亏损{state.monthly_pnl:.1%}超{abs(self.L3_monthly):.0%}", 0.0
        # L2
        if state.weekly_pnl <= self.L2_weekly:
            return True, f"L2: 周亏损{state.weekly_pnl:.1%}→降仓50%", proposed_position * 0.5
        # L1
        if state.daily_pnl <= self.L1_daily:
            return True, f"L1: 日亏损{state.daily_pnl:.1%}→禁止新仓", 0.0
        # L5
        sector_exp = state.sector_exposures.get(symbol, 0.0) + proposed_position
        if sector_exp > self.L5_sector:
            return False, f"L5: 单板块{sector_exp:.0%}超{self.L5_sector:.0%}", 0.0
        # L6
        new_total = state.total_exposure + proposed_position
        if new_total > self.L6_total:
            return False, f"L6: 总仓位{new_total:.0%}超{self.L6_total:.0%}", 0.0
        # 连续亏损保护
        if state.consecutive_losses >= 5:
            return False, "连续5次亏损→暂停交易", 0.0
        if state.consecutive_losses >= 3:
            return True, "连续3次亏损→仓位减半", proposed_position * 0.5

        return True, "通过", proposed_position


def kelly_criterion(win_prob: float, win_loss_ratio: float, fraction: float = 0.25) -> float:
    """凯利公式 — §6.1.3

    f* = (p*b - q) / b
    position ≤ fraction * f*
    """
    if win_loss_ratio <= 0:
        return 0.0
    f_star = (win_prob * win_loss_ratio - (1.0 - win_prob)) / win_loss_ratio
    if f_star <= 0:
        return 0.0
    return fraction * f_star


def kelly_position(win_prob: float, r_r_ratio: float,
                   fraction: float = 0.25,
                   min_rr: float = 1.0) -> float:
    """凯利仓位计算 — §6.1.3

    含R:R过滤器: R:R>=1才允许交易
    """
    if r_r_ratio < min_rr:
        return 0.0
    return kelly_criterion(win_prob, r_r_ratio, fraction)
