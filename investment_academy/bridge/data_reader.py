"""SPAS 数据读取适配器 — 唯一访问 Parquet ETF 数据的地方"""
import os
from pathlib import Path
from typing import Optional

import pandas as pd

# SPAS 项目根目录（向上两级：bridge/ -> investment_academy/ -> D:\stock_market\）
SPAS_ROOT = Path(__file__).resolve().parent.parent.parent
SPAS_DATA_DIR = SPAS_ROOT / "data"


def list_available_etfs() -> list[dict]:
    """列出 data/ 中所有可用的 ETF Parquet 文件"""
    etfs = []
    if not SPAS_DATA_DIR.exists():
        return etfs
    for f in sorted(SPAS_DATA_DIR.glob("*_day.parquet")):
        code = f.stem.replace("_day", "")
        etfs.append({
            "code": code,
            "market": "SH" if ".SH" in f.stem else "SZ",
            "file": str(f),
            "has_5min": (SPAS_DATA_DIR / f"{code}_5min.parquet").exists(),
        })
    return etfs


def load_etf_data(code: str, timeframe: str = "day") -> Optional[pd.DataFrame]:
    """加载指定 ETF 的数据

    Args:
        code: ETF 代码，如 '512480.SH' 或 '510300.SH'
        timeframe: 'day' 或 '5min'

    Returns:
        DataFrame with OHLCV columns sorted by trade_date, or None if not found
    """
    file_path = SPAS_DATA_DIR / f"{code}_{timeframe}.parquet"
    if not file_path.exists():
        files = list(SPAS_DATA_DIR.glob(f"{code}*.parquet"))
        if files:
            file_path = files[0]
        else:
            return None

    df = pd.read_parquet(file_path)

    # 标准化列名
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().replace("_", "")
        if col_lower in ("tradedate", "trade_date", "date", "datetime", "timestamp"):
            col_map[col] = "trade_date"
        elif col_lower in ("open",):
            col_map[col] = "open"
        elif col_lower in ("high",):
            col_map[col] = "high"
        elif col_lower in ("low",):
            col_map[col] = "low"
        elif col_lower in ("close",):
            col_map[col] = "close"
        elif col_lower in ("vol", "volume"):
            col_map[col] = "volume"

    df = df.rename(columns=col_map)
    required_cols = ["trade_date", "open", "high", "low", "close", "volume"]
    available_cols = [c for c in required_cols if c in df.columns]

    if not available_cols:
        return df

    return df[available_cols].sort_values("trade_date").reset_index(drop=True)


def load_all_etf_metadata() -> pd.DataFrame:
    """加载所有 ETF 的元数据概览（代码、行数、起止日期）"""
    etfs = list_available_etfs()
    records = []
    for etf in etfs:
        df = load_etf_data(etf["code"], "day")
        if df is not None and len(df) > 0:
            records.append({
                "code": etf["code"],
                "market": etf["market"],
                "rows": len(df),
                "start_date": str(df["trade_date"].iloc[0])[:10] if "trade_date" in df.columns else "N/A",
                "end_date": str(df["trade_date"].iloc[-1])[:10] if "trade_date" in df.columns else "N/A",
            })
    return pd.DataFrame(records) if records else pd.DataFrame()


def get_etf_close_series(code: str, timeframe: str = "day") -> Optional[pd.Series]:
    """获取 ETF 收盘价序列（用于快速绘图）"""
    df = load_etf_data(code, timeframe)
    if df is None or "trade_date" not in df.columns or "close" not in df.columns:
        return None
    return df.set_index("trade_date")["close"]


class DataNotAvailableError(Exception):
    """数据不可用异常"""
    pass
