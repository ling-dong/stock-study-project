"""§4.1.3 分钟级复权处理"""
from datetime import date
from decimal import Decimal
import pandas as pd


class PriceAdjuster:
    """分钟级前复权价格计算器 — P_adj_min = P_raw_min × factor_t / factor_base"""

    def __init__(self):
        self._daily_factors: dict = {}

    def set_daily_factors(self, symbol: str, factors: dict, base_date: date = None):
        self._daily_factors[symbol] = factors
        self._base_date = base_date

    def adjust_price(self, symbol: str, raw_price: Decimal,
                     trade_date: date) -> Decimal:
        factors = self._daily_factors.get(symbol, {})
        factor_t = factors.get(trade_date)
        if factor_t is None:
            return Decimal("NaN")
        base_factor = list(factors.values())[0] if factors else Decimal("1")
        if base_factor == 0:
            return Decimal("NaN")
        return raw_price * factor_t / base_factor

    def adjust_dataframe(self, symbol: str, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in ["open", "high", "low", "close"]:
            if col in df.columns and "trade_date" in df.columns:
                df[col] = df.apply(
                    lambda row: float(self.adjust_price(
                        symbol, Decimal(str(row[col])), row["trade_date"].date()
                    )), axis=1
                )
        return df
