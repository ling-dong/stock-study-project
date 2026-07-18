"""本地Parquet缓存适配器 — 第一优先级(零延迟)"""
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.data.adapters.base import DataAdapter


class LocalAdapter(DataAdapter):
    source_name = "local"

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def get_bars(self, symbol: str, freq: str,
                       start: datetime = None, end: datetime = None) -> pd.DataFrame:
        file_path = self.data_dir / f"{symbol}_{freq}.parquet"
        if not file_path.exists():
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])
        df = pd.read_parquet(file_path)
        if df.empty:
            return df

        # 统一时间列名
        time_cols = [c for c in df.columns if c.lower() in ("timestamp", "trade_date", "date")]
        if time_cols:
            df = df.rename(columns={time_cols[0]: "timestamp"})
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            if start: df = df[df["timestamp"] >= start]
            if end: df = df[df["timestamp"] <= end]
        return df

    async def save_bars(self, symbol: str, freq: str, df: pd.DataFrame):
        file_path = self.data_dir / f"{symbol}_{freq}.parquet"
        df.to_parquet(file_path, index=False)

    async def health_check(self) -> bool:
        return self.data_dir.exists()
