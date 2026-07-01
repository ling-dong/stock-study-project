"""市场数据 — Bridge 层 ETF 数据接口"""
from fastapi import APIRouter, HTTPException, Query
from bridge.data_reader import (
    list_available_etfs,
    load_etf_data,
    load_all_etf_metadata,
    get_etf_display_name,
)

router = APIRouter(prefix="/api/market", tags=["市场数据"])


@router.get("/etfs")
def get_etfs():
    """可用 ETF 列表"""
    return list_available_etfs()


@router.get("/etfs/meta")
def get_etfs_metadata():
    """ETF 元数据总览"""
    meta = load_all_etf_metadata()
    if meta.empty:
        return []
    return meta.to_dict(orient="records")


@router.get("/etf/{code}/name")
def get_etf_name(code: str):
    """ETF 友好显示名"""
    return {
        "code": code,
        "display_name": get_etf_display_name(code),
    }


@router.get("/etf/{code}/ohlcv")
def get_etf_ohlcv(
    code: str,
    tf: str = Query("day", alias="tf"),
    limit: int = Query(180, ge=1, le=2000),
):
    """ETF OHLCV 数据（K线图用）"""
    df = load_etf_data(code, tf)
    if df is None:
        raise HTTPException(status_code=404, detail=f"ETF 数据不存在: {code}")

    # 取最近 N 条
    df = df.tail(limit)

    # DataFrame → JSON
    bars = []
    for _, row in df.iterrows():
        bar = {"date": str(row["trade_date"])[:10]}
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                val = float(row[col])
                bar[col] = val
        bars.append(bar)

    return {
        "code": code,
        "timeframe": tf,
        "bars": bars,
    }
