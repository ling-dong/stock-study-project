"""Tushare Pro适配器 — 主力数据源(第二优先级)"""
from datetime import datetime
import pandas as pd
from src.data.adapters.base import DataAdapter


class TushareAdapter(DataAdapter):
    source_name = "tushare"

    def __init__(self, token: str = None):
        self.token = token
        self._healthy = True

    async def get_bars(self, symbol: str, freq: str,
                       start: datetime = None, end: datetime = None) -> pd.DataFrame:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_check(self) -> bool:
        return self._healthy
