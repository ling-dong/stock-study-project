"""§6.2 尾部风险应对 — 黑天鹅触发器 + 熔断记忆"""


class TailRiskManager:
    """尾部风险管理 — §6.2.1, §6.2.3"""

    def __init__(self):
        self._recent_crash_days: set = set()
        self._circuit_breaker_active: bool = False
        self._circuit_breaker_days_remaining: int = 0

    def check_black_swan(self, vix_percentile: float, daily_sector_decline: float,
                         single_day_drop: float, gap_pct: float) -> tuple:
        """黑天鹅检测

        Returns: (triggered, action)
        """
        # VIX>95%分位或板块单日跌幅>5%
        if vix_percentile > 0.95 or abs(daily_sector_decline) > 0.05:
            return True, "黑天鹅: 仓位强制降至10%"

        # 跳空>3%
        if abs(gap_pct) > 0.03:
            return True, "跳空>3%: 清仓并暂停24h"

        # 单日跌幅>7%
        if abs(single_day_drop) > 0.07:
            return True, "单日跌幅>7%: 熔断暂停该类Setup"

        return False, None

    def record_crash(self, date_str: str):
        self._recent_crash_days.add(date_str)

    def is_frozen(self, date_str: str, lookback_days: int = 5) -> bool:
        """熔断记忆: 过去5天出现过跌停则暂停"""
        return date_str in self._recent_crash_days


class CircuitBreaker:
    """熔断机制 — §6.2.3"""

    def __init__(self):
        self.active = False
        self.pause_until = None
        self.reduction_level = 0.0  # 0=none, 0.5=half, 1.0=full

    def trigger(self, reduction: float, pause_hours: int = 24):
        from datetime import datetime, timedelta
        self.active = True
        self.reduction_level = reduction
        self.pause_until = datetime.now() + timedelta(hours=pause_hours)

    def reset(self):
        self.active = False
        self.reduction_level = 0.0
        self.pause_until = None

    def get_position_multiplier(self) -> float:
        if not self.active:
            return 1.0
        if self.pause_until and self.pause_until > datetime.now():
            return 1.0 - self.reduction_level
        return 1.0
