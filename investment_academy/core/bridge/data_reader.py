"""SPAS 数据读取适配器 — 唯一访问 Parquet ETF 数据的地方"""
import os
from pathlib import Path
from typing import Optional
import yaml

import pandas as pd

from core.utils.path_utils import validate_etf_code, validate_timeframe

# SPAS 项目根目录：bridge/ -> investment_academy/ -> 项目根目录
SPAS_ROOT = Path(__file__).resolve().parent.parent.parent.parent
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
    if not validate_etf_code(code) or not validate_timeframe(timeframe):
        return None

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


_ETF_NAME_CACHE = None


def get_etf_name_map() -> dict[str, str]:
    """获取 ETF 代码 → 友好名称的映射

    来源：sectors.yaml + 内置宽基ETF名称

    Returns:
        {'512480.SH': '半导体ETF', '510300.SH': '沪深300ETF', ...}
    """
    global _ETF_NAME_CACHE
    if _ETF_NAME_CACHE is not None:
        return _ETF_NAME_CACHE

    mapping = {}

    # 1. 从 sectors.yaml 提取
    sectors_path = SPAS_ROOT / "config" / "sectors.yaml"
    if sectors_path.exists():
        with open(sectors_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for s in data.get("sectors", []):
            code = s.get("etf_code", "")
            name = s.get("name", "")
            if code and name:
                mapping[code] = f"{name}ETF"

    # 2. 宽基 ETF 手动补全
    broad = {
        "512100.SH": "中证1000ETF",
        "510300.SH": "沪深300ETF",
        "510050.SH": "上证50ETF",
        "159915.SZ": "创业板ETF",
        "588000.SH": "科创50ETF",
        "512880.SH": "证券ETF",
        "515000.SH": "科技ETF",
        "515250.SH": "智能汽车ETF",
        "516100.SH": "金融科技ETF",
        "516980.SH": "化工ETF",
        "159739.SZ": "大数据ETF",
        "159783.SZ": "双创ETF",
        "159852.SZ": "软件ETF",
    }
    for code, name in broad.items():
        if code not in mapping:
            mapping[code] = name

    _ETF_NAME_CACHE = mapping
    return mapping


def get_etf_display_name(code: str) -> str:
    """获取 ETF 的友好显示名

    Args:
        code: ETF 代码，如 '512480.SH'
    Returns:
        如 '512480.SH  半导体ETF'
    """
    names = get_etf_name_map()
    name = names.get(code, "")
    if name:
        return f"{code}  {name}"
    return code


class DataNotAvailableError(Exception):
    """数据不可用异常"""
    pass
