"""交易沙盒 — 内存会话管理"""
import uuid
import threading
from fastapi import APIRouter, HTTPException
from core.bridge.data_reader import load_etf_data
from core.engine.sandbox_engine import SandboxEngine
from core.utils.path_utils import validate_etf_code, validate_timeframe
from backend.schemas import (
    SandboxInitIn, SandboxInitOut,
    SandboxBuyIn, SandboxSellIn,
)

router = APIRouter(prefix="/api/sandbox", tags=["交易沙盒"])

# 内存会话存储器
import time as _time
_sessions: dict[str, SandboxEngine] = {}
_sessions_ts: dict[str, float] = {}  # session_id → 创建时间戳
_lock = threading.Lock()
SESSION_TTL = 1800  # 30 分钟超时自动清理


def _cleanup_expired():
    """清理过期会话"""
    now = _time.time()
    expired = [sid for sid, ts in _sessions_ts.items() if now - ts > SESSION_TTL]
    for sid in expired:
        _sessions.pop(sid, None)
        _sessions_ts.pop(sid, None)


@router.post("/init", response_model=SandboxInitOut)
def sandbox_init(body: SandboxInitIn):
    """初始化沙盒会话"""
    if not validate_etf_code(body.etf_code) or not validate_timeframe(body.timeframe):
        raise HTTPException(status_code=400, detail="非法的 ETF 代码或时间周期")
    df = load_etf_data(body.etf_code, body.timeframe)
    if df is None or len(df) == 0:
        raise HTTPException(status_code=404, detail=f"ETF 数据不存在: {body.etf_code}")

    # 按起始日期过滤
    if body.start_date and "trade_date" in df.columns:
        df = df[df["trade_date"] >= body.start_date]
        if len(df) == 0:
            raise HTTPException(status_code=400, detail=f"起始日期 {body.start_date} 之后无数据")
        df = df.reset_index(drop=True)

    engine = SandboxEngine(df, initial_cash=body.initial_cash)
    session_id = uuid.uuid4().hex[:12]

    with _lock:
        _cleanup_expired()
        _sessions[session_id] = engine
        _sessions_ts[session_id] = _time.time()

    return {"session_id": session_id, "total_bars": len(df)}


def _get_engine(session_id: str) -> SandboxEngine:
    """获取沙盒引擎，不存在则 404"""
    with _lock:
        engine = _sessions.get(session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="沙盒会话不存在或已过期")
    return engine


@router.get("/{session_id}/state")
def sandbox_state(session_id: str):
    """获取沙盒当前状态"""
    e = _get_engine(session_id)
    return {
        "session_id": session_id,
        "cash": e.state.cash,
        "shares": e.state.shares,
        "cost_basis": e.state.cost_basis,
        "index": e.state.current_index,
        "total_bars": e.state.total_bars,
        "is_done": e.is_done,
    }


@router.get("/{session_id}/bar")
def sandbox_bar(session_id: str):
    """获取当前 K 线"""
    e = _get_engine(session_id)
    bar = e.current_bar
    if bar is None:
        raise HTTPException(status_code=400, detail="回测已结束，无更多数据")
    return bar


@router.post("/{session_id}/advance")
def sandbox_advance(session_id: str):
    """前进到下一根 bar"""
    e = _get_engine(session_id)
    bar = e.advance()
    return {"bar": bar, "is_done": e.is_done}


@router.get("/{session_id}/can-buy")
def sandbox_can_buy(session_id: str):
    """检查能否买入"""
    e = _get_engine(session_id)
    can, msg = e.can_buy()
    return {"can": can, "message": msg}


@router.post("/{session_id}/buy")
def sandbox_buy(session_id: str, body: SandboxBuyIn):
    """执行买入"""
    e = _get_engine(session_id)
    trade = e.buy(shares=body.shares, reason=body.reason)
    if trade is None:
        can, msg = e.can_buy()
        raise HTTPException(status_code=400, detail=msg)
    bar = e.current_bar
    return {
        "trade": {
            "date": trade.date,
            "action": trade.action,
            "price": trade.price,
            "shares": trade.shares,
            "amount": trade.amount,
            "reason": trade.reason,
            "cost": trade.cost,
        },
        "bar": bar,
    }


@router.get("/{session_id}/can-sell")
def sandbox_can_sell(session_id: str):
    """检查能否卖出"""
    e = _get_engine(session_id)
    can, msg = e.can_sell()
    return {"can": can, "message": msg}


@router.post("/{session_id}/sell")
def sandbox_sell(session_id: str, body: SandboxSellIn):
    """执行卖出"""
    e = _get_engine(session_id)
    shares = body.shares if body.shares > 0 else e.state.shares
    trade = e.sell(shares=shares, reason=body.reason)
    if trade is None:
        can, msg = e.can_sell()
        raise HTTPException(status_code=400, detail=msg)
    bar = e.current_bar
    return {
        "trade": {
            "date": trade.date,
            "action": trade.action,
            "price": trade.price,
            "shares": trade.shares,
            "amount": trade.amount,
            "reason": trade.reason,
            "cost": trade.cost,
        },
        "bar": bar,
    }


@router.get("/{session_id}/portfolio")
def sandbox_portfolio(session_id: str):
    """获取组合状态"""
    e = _get_engine(session_id)
    bar = e.current_bar
    return {
        "cash": e.state.cash,
        "shares": e.state.shares,
        "price": bar["close"] if bar else 0,
        "value": e.get_portfolio_value(),
        "unrealized_pnl": e.get_unrealized_pnl(),
        "unrealized_pnl_pct": e.get_unrealized_pnl_pct(),
        "cost_basis": e.get_current_cost_basis(),
    }


@router.get("/{session_id}/performance")
def sandbox_performance(session_id: str):
    """获取完整绩效报告"""
    e = _get_engine(session_id)
    report = e.get_performance()
    return {
        "initial_cash": report.initial_cash,
        "final_cash": report.final_cash,
        "final_shares": report.final_shares,
        "final_price": report.final_price,
        "total_value": report.total_value,
        "total_return_pct": report.total_return_pct,
        "total_trades": report.total_trades,
        "winning_trades": report.winning_trades,
        "losing_trades": report.losing_trades,
        "win_rate": report.win_rate,
        "max_drawdown_pct": report.max_drawdown_pct,
        "total_costs": report.total_costs,
        "trades": [
            {
                "date": t.date,
                "action": t.action,
                "price": t.price,
                "shares": t.shares,
                "amount": t.amount,
                "reason": t.reason,
                "cost": t.cost,
            }
            for t in report.trades
        ],
    }


@router.get("/{session_id}/equity-curve")
def sandbox_equity_curve(session_id: str):
    """获取权益曲线"""
    e = _get_engine(session_id)
    curve = e.get_equity_curve()
    if curve.empty:
        return []
    return curve.to_dict(orient="records")
