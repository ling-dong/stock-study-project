"""§4.5.3 网络Exhaustion指数"""
from typing import List


class ExhaustionIndex:
    """网络衰竭指数 — §4.5.3

    综合计算板块内部与板块间关联的双重疲惫信号。
    需连续3-5个交易日确认，不独立触发交易。
    """
    def __init__(self, confirmation_days: int = 3, correlation_warning: float = 0.8):
        self.confirmation_days = confirmation_days
        self.correlation_warning = correlation_warning
        self._daily_readings: List[float] = []

    def compute(self, sector_returns: dict[str, float], linked_returns: dict[str, float]) -> float:
        """计算Exhaustion指数 [0, 1]"""
        if not sector_returns or not linked_returns:
            return 0.0

        # 简化: 板块和关联板块同步衰竭的比例
        synced = sum(1 for s, r in sector_returns.items()
                     if r < 0 and linked_returns.get(s, 0) < 0)
        total = len(sector_returns)
        ratio = synced / total if total > 0 else 0.0

        self._daily_readings.append(ratio)
        if len(self._daily_readings) > 10:
            self._daily_readings = self._daily_readings[-10:]

        return ratio

    def is_confirmed(self) -> bool:
        """连续N天确认"""
        if len(self._daily_readings) < self.confirmation_days:
            return False
        return all(r > 0.5 for r in self._daily_readings[-self.confirmation_days:])

    def is_warning(self, avg_correlation: float) -> bool:
        return avg_correlation > self.correlation_warning
