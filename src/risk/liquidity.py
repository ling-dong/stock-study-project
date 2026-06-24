"""§6.2.2 流动性分层监控"""


class LiquidityMonitor:
    """三层流动性监控 — §6.2.2"""

    def __init__(self, max_spread_multiplier: float = 3.0,
                 max_premium_pct: float = 0.02,
                 max_discount_pct: float = 0.03,
                 max_position_daily_volume_pct: float = 0.05):
        self.max_spread_multiplier = max_spread_multiplier
        self.max_premium_pct = max_premium_pct
        self.max_discount_pct = max_discount_pct
        self.max_position_daily_volume_pct = max_position_daily_volume_pct

    def check_spread(self, current_spread: float, normal_spread: float) -> tuple:
        """Layer 1: 买卖价差检查"""
        if normal_spread > 0 and current_spread > self.max_spread_multiplier * normal_spread:
            return False, f"价差异常: {current_spread:.4f} > {self.max_spread_multiplier}*正常"
        return True, "价差正常"

    def check_premium(self, etf_price: float, nav: float) -> tuple:
        """Layer 2: ETF折溢价检查"""
        if nav <= 0:
            return True, "无NAV"
        premium = (etf_price - nav) / nav
        if premium > self.max_premium_pct:
            return False, f"溢价{premium:.1%}超{self.max_premium_pct:.0%}→停止买入"
        if premium < -self.max_discount_pct:
            return False, f"折价{abs(premium):.1%}超{self.max_discount_pct:.0%}→停止卖出"
        return True, "折溢价正常"

    def check_position_size(self, position_value: float, daily_volume: float) -> tuple:
        """Layer 3: 持仓流动性"""
        if daily_volume <= 0:
            return False, "无成交量数据"
        ratio = position_value / daily_volume
        if ratio > self.max_position_daily_volume_pct:
            return False, f"持仓{ratio:.1%}超日均成交量{self.max_position_daily_volume_pct:.0%}"
        return True, "流动性充足"
