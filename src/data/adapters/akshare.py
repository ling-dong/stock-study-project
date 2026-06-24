"""AKShare适配器 — 备用数据源(第三优先级)"""
from datetime import datetime
import pandas as pd
from src.data.adapters.base import DataAdapter


class AKShareAdapter(DataAdapter):
    source_name = "akshare"

    def __init__(self):
        self._healthy = True

    async def get_bars(self, symbol: str, freq: str,
                       start: datetime = None, end: datetime = None) -> pd.DataFrame:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_check(self) -> bool:
        return self._healthy
