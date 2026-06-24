"""§7.3 REST API — 信号查询 + 系统状态"""
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn


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


def create_app(orchestrator=None) -> FastAPI:
    app = FastAPI(title="SPAS API", version="0.1.0")

    @app.get("/signals/latest", response_model=SignalResponse)
    async def latest_signal():
        if orchestrator is None:
            return {"symbol": "N/A", "timestamp": "", "setup_type": "", "direction_prob": 0,
                    "target_prob": 0, "stop_prob": 0, "r_r_ratio": 0, "expected_value": 0,
                    "confidence_level": "N/A"}
        sig = orchestrator.get_latest_signal()
        if sig is None:
            return {"symbol": "N/A", "timestamp": "", "setup_type": "", "direction_prob": 0,
                    "target_prob": 0, "stop_prob": 0, "r_r_ratio": 0, "expected_value": 0,
                    "confidence_level": "N/A"}
        return SignalResponse(
            symbol=sig.symbol, timestamp=sig.timestamp.isoformat() if sig.timestamp else "",
            setup_type=sig.setup_type, direction_prob=float(sig.direction_prob),
            target_prob=float(sig.target_prob), stop_prob=float(sig.stop_prob),
            r_r_ratio=float(sig.r_r_ratio), expected_value=float(sig.expected_value),
            confidence_level=sig.confidence_level,
        )

    @app.get("/signals/history")
    async def signal_history(limit: int = Query(default=20, le=100)):
        if orchestrator is None:
            return {"signals": [], "count": 0}
        signals = orchestrator.get_signals(limit)
        return {
            "signals": [{
                "symbol": s.symbol, "setup_type": s.setup_type,
                "direction_prob": float(s.direction_prob),
                "timestamp": s.timestamp.isoformat() if s.timestamp else "",
            } for s in signals],
            "count": len(signals),
        }

    @app.get("/system/status", response_model=SystemStatus)
    async def system_status():
        if orchestrator is None:
            return SystemStatus()
        latest = orchestrator.get_latest_signal()
        return SystemStatus(
            last_signal_time=latest.timestamp.isoformat() if latest and latest.timestamp else None,
            total_signals=len(orchestrator.get_signals(1000)),
        )

    @app.get("/system/version")
    async def system_version():
        return {"version": "System_v0.1={rules_v1,model_v1,features_v1,data_v1}"}

    return app
