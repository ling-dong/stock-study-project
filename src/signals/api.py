"""§7.3 REST API — SPAS 核心引擎统一对外接口

端点：
- /api/spas/signal/{code}   对指定 ETF 运行完整 SPAS 流水线
- /api/spas/market/etfs     可用 ETF 列表
- /api/spas/market/etf/{code}/ohlcv  OHLCV 数据
- /api/spas/market/etfs/meta        ETF 元数据
- /api/spas/system/status   系统状态
- /signals/latest (兼容)   最新信号（内存中）
- /signals/history (兼容)  历史信号（内存中）
"""
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from src.signals.service import SPASService


class SignalResponse(BaseModel):
    symbol: str
    timestamp: str
    setup_type: str
    direction_prob: float
    target_prob: float
    stop_prob: float
    r_r_ratio: float
    expected_value: float
    confidence_level: str


class SystemStatus(BaseModel):
    status: str = "running"
    version: str = "System_v0.1"
    last_signal_time: Optional[str] = None
    total_signals: int = 0


class MarketStateOut(BaseModel):
    state: Optional[str]
    confidence: Optional[float]
    duration: Optional[int]


class SetupSummaryOut(BaseModel):
    confirmed_count: int
    candidate_count: int
    latest_confirmed_date: Optional[str]
    latest_candidate_date: Optional[str]


class PredictionOut(BaseModel):
    direction_prob: float
    target_prob: float
    stop_prob: float
    r_r_ratio: float
    expected_value: float
    confidence_level: str
    setup_type: str


class RiskOut(BaseModel):
    kelly_position: float
    risk_ok: bool
    risk_reason: str


class SPASAnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    current_price: float
    market_state: MarketStateOut
    setup_summary: SetupSummaryOut
    prediction: Optional[PredictionOut]
    risk: Optional[RiskOut]


class OHLCVBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class ETFMeta(BaseModel):
    code: str
    market: str
    rows: int
    start_date: str
    end_date: str


def create_app(service: Optional[SPASService] = None) -> FastAPI:
    app = FastAPI(title="SPAS API", version="0.1.0")
    svc = service or SPASService()

    # ═══════════════════════════════════════════════════════════
    # 新版 SPAS 核心端点
    # ═══════════════════════════════════════════════════════════

    @app.get("/api/spas/signal/{code}", response_model=SPASAnalysisResponse)
    async def spas_signal(code: str):
        """对指定 ETF 运行完整 SPAS 流水线并返回最新信号"""
        result = await svc.analyze_etf(code)
        if result is None:
            raise HTTPException(status_code=404, detail=f"ETF 数据不足或不存在: {code}")
        return {
            "symbol": result.symbol,
            "timestamp": result.timestamp.isoformat(),
            "current_price": result.current_price,
            "market_state": result.market_state,
            "setup_summary": result.setup_summary,
            "prediction": result.prediction,
            "risk": result.risk,
        }

    @app.get("/api/spas/market/etfs")
    async def market_etfs():
        """可用 ETF 列表"""
        return await svc.list_etfs()

    @app.get("/api/spas/market/etfs/meta", response_model=List[ETFMeta])
    async def market_etfs_meta():
        """ETF 元数据概览"""
        return await svc.get_etf_metadata()

    @app.get("/api/spas/market/etf/{code}/ohlcv")
    async def market_etf_ohlcv(
        code: str,
        freq: str = Query("day", description="时间框架: day / 5min"),
        limit: int = Query(180, ge=1, le=2000, description="返回最近 N 条"),
    ):
        """ETF OHLCV 数据（K线图用）"""
        bars = await svc.get_ohlcv(code, freq, limit)
        if not bars:
            raise HTTPException(status_code=404, detail=f"ETF 数据不存在: {code}")
        return {"code": code, "timeframe": freq, "bars": bars}

    @app.get("/api/spas/system/status")
    async def spas_system_status():
        """SPAS 系统状态"""
        return svc.get_system_status()

    # ═══════════════════════════════════════════════════════════
    # 兼容旧版端点（基于内存信号，未来可移除）
    # ═══════════════════════════════════════════════════════════

    _latest_signals: List[SignalResponse] = []
    _signal_count: int = 0

    @app.get("/signals/latest", response_model=SignalResponse)
    async def latest_signal():
        if not _latest_signals:
            return {"symbol": "N/A", "timestamp": "", "setup_type": "",
                    "direction_prob": 0, "target_prob": 0, "stop_prob": 0,
                    "r_r_ratio": 0, "expected_value": 0, "confidence_level": "N/A"}
        sig = _latest_signals[-1]
        return sig

    @app.get("/signals/history")
    async def signal_history(limit: int = Query(default=20, le=100)):
        return {"signals": [_latest_signals[-i].dict() for i in range(1, min(limit + 1, len(_latest_signals) + 1))],
                "count": len(_latest_signals)}

    @app.get("/system/status", response_model=SystemStatus)
    async def system_status():
        return SystemStatus()

    @app.get("/system/version")
    async def system_version():
        return {"version": "System_v0.1={rules_v1,model_v1,features_v1,data_v1}"}

    return app
