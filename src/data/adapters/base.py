"""§4.1.1 UDAI统一数据抽象接口"""
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd


class DataAdapter(ABC):
    """统一数据抽象接口 — 屏蔽Tushare/AKShare/本地三源差异"""
    source_name: str = "base"

    @abstractmethod
    async def get_bars(
        self, symbol: str, freq: str,
        start: datetime = None, end: datetime = None,
    ) -> pd.DataFrame:
        """获取K线数据 — 返回标准化DataFrame(open/high/low/close/volume/factor)"""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查 — 心跳检测(30秒间隔)"""
        ...
