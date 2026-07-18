"""SPAS 预测 — Academy 后端代理

所有真实预测逻辑由 SPAS 核心 API (port 8000) 处理。
本路由仅做请求转发和响应适配，不实现任何预测算法。
"""
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException


SPAS_API_BASE = os.environ.get("SPAS_API_URL", "http://127.0.0.1:8000/api/spas")

router = APIRouter(prefix="/api/spas", tags=["SPAS 自动信号"])


async def _forward_get(path: str, params: Optional[dict] = None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(f"{SPAS_API_BASE}/{path}", params=params)
        except httpx.ConnectError as e:
            raise HTTPException(status_code=503, detail=f"SPAS API 未启动: {e}")
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


async def _forward_post(path: str, body: dict):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(f"{SPAS_API_BASE}/{path}", json=body)
        except httpx.ConnectError as e:
            raise HTTPException(status_code=503, detail=f"SPAS API 未启动: {e}")
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@router.get("/signal/{code}")
async def spas_signal(code: str):
    """获取指定 ETF 的 SPAS 自动信号"""
    return await _forward_get(f"signal/{code}")


@router.get("/market/etfs")
async def market_etfs():
    """可用 ETF 列表"""
    return await _forward_get("market/etfs")


@router.get("/market/etfs/meta")
async def market_etfs_meta():
    """ETF 元数据"""
    return await _forward_get("market/etfs/meta")


@router.get("/market/etf/{code}/ohlcv")
async def market_etf_ohlcv(code: str, freq: str = "day", limit: int = 180):
    """ETF OHLCV 数据"""
    return await _forward_get(f"market/etf/{code}/ohlcv", {"freq": freq, "limit": limit})


@router.get("/system/status")
async def system_status():
    """SPAS 系统状态"""
    return await _forward_get("system/status")
