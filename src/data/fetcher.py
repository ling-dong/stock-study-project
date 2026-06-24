"""§4.1.1 多源数据协调器 — 健康状态机 + 主备自动切换"""
from datetime import datetime
import asyncio
import logging
import pandas as pd
from src.data.adapters.base import DataAdapter
from src.data.adapters.local import LocalAdapter
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.akshare import AKShareAdapter

logger = logging.getLogger(__name__)


class DataFetcher:
    """多数据源协调器 — 优先级: 本地 > Tushare > AKShare"""

    def __init__(self):
        self.adapters: list = []
        self._health_status: dict = {}
        self._failure_threshold = 3

    def register(self, adapter: DataAdapter, priority: int):
        self.adapters.append((priority, adapter))
        self.adapters.sort(key=lambda x: x[0])
        self._health_status[adapter.source_name] = 0

    @classmethod
    def with_defaults(cls, data_dir: str = "data") -> "DataFetcher":
        fetcher = cls()
        fetcher.register(LocalAdapter(data_dir), priority=0)
        fetcher.register(TushareAdapter(), priority=1)
        fetcher.register(AKShareAdapter(), priority=2)
        return fetcher

    async def get_bars(self, symbol: str, freq: str,
                       start: datetime = None, end: datetime = None) -> pd.DataFrame:
        for _, adapter in self.adapters:
            if self._health_status.get(adapter.source_name, 0) >= self._failure_threshold:
                continue
            try:
                df = await adapter.get_bars(symbol, freq, start, end)
                self._health_status[adapter.source_name] = 0
                if df.empty and adapter.source_name != "local":
                    continue
                return df
            except Exception as e:
                self._health_status[adapter.source_name] = (
                    self._health_status.get(adapter.source_name, 0) + 1
                )
                logger.error(f"Adapter {adapter.source_name} failed: {e}")
                continue
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_monitor(self):
        while True:
            for _, adapter in self.adapters:
                try:
                    healthy = await adapter.health_check()
                    if not healthy:
                        self._health_status[adapter.source_name] += 1
                    else:
                        self._health_status[adapter.source_name] = 0
                except Exception:
                    self._health_status[adapter.source_name] += 1
            await asyncio.sleep(30)
