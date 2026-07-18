"""用户系统 — 偏好 + 心理自检 + 交易日志"""
from fastapi import APIRouter, HTTPException
import json
from core.db.repository import (
    get_user_preferences,
    save_user_preferences,
    save_psychology_check,
    get_psychology_history,
    save_journal_entry,
    get_journal_entries,
    get_journal_entry,
    update_journal_entry,
    delete_journal_entry,
)
from backend.schemas import (
    UserPreferencesIn,
    PsychologyCheckIn,
    TradingJournalIn,
)

router = APIRouter(prefix="/api/user", tags=["用户系统"])


def _parse_achievements(raw) -> list:
    """将 JSON 字符串或 list 统一转为 list"""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    if isinstance(raw, list):
        return raw
    return []


@router.get("/preferences")
def get_preferences():
    """获取用户偏好"""
    prefs = get_user_preferences()
    prefs["achievements"] = _parse_achievements(prefs.get("achievements", []))
    return prefs


@router.put("/preferences")
def update_preferences(body: UserPreferencesIn):
    """更新用户偏好"""
    save_user_preferences(body.model_dump())
    return get_preferences()


@router.post("/psychology-check")
def add_psychology_check(body: PsychologyCheckIn):
    """记录心理自检"""
    row_id = save_psychology_check(
        scores=body.scores,
        overall_risk_level=body.overall_risk_level,
        proceeded_to_trade=body.proceeded_to_trade,
        self_notes=body.self_notes,
    )
    return {"id": row_id}


@router.get("/psychology-history")
def list_psychology_history():
    """心理自检历史"""
    return get_psychology_history()


@router.post("/journal")
def add_journal_entry(body: TradingJournalIn):
    """记录交易日志"""
    row_id = save_journal_entry(body.model_dump())
    return {"id": row_id}


@router.get("/journal")
def list_journal():
    """交易日志列表"""
    return get_journal_entries()


@router.put("/journal/{entry_id}")
def edit_journal_entry(entry_id: int, body: TradingJournalIn):
    """编辑交易日志"""
    existing = get_journal_entry(entry_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="日志不存在")
    ok = update_journal_entry(entry_id, body.model_dump())
    if not ok:
        raise HTTPException(status_code=500, detail="更新失败")
    return get_journal_entry(entry_id)


@router.delete("/journal/{entry_id}")
def remove_journal_entry(entry_id: int):
    """删除交易日志"""
    existing = get_journal_entry(entry_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="日志不存在")
    delete_journal_entry(entry_id)
    return {"deleted": True}
