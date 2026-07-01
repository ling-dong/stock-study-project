"""学习进度 — CRUD"""
from fastapi import APIRouter, HTTPException
from db.repository import (
    get_all_chapter_progress,
    get_chapter_progress,
    save_chapter_progress,
)
from backend.schemas import ChapterProgressOut, ChapterProgressUpdateIn
from datetime import datetime

router = APIRouter(prefix="/api/progress", tags=["学习进度"])


@router.get("")
def list_progress():
    """全部章节进度"""
    rows = get_all_chapter_progress()
    return rows


@router.get("/{chapter_id}")
def get_progress(chapter_id: str):
    """单个章节进度"""
    row = get_chapter_progress(chapter_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"未找到进度: {chapter_id}")
    return row


@router.post("/{chapter_id}")
def update_progress(chapter_id: str, body: ChapterProgressUpdateIn):
    """更新章节进度"""
    timestamp = datetime.now().isoformat()
    save_chapter_progress(
        chapter_id=chapter_id,
        completed=body.completed,
        quiz_score=body.quiz_score,
        quiz_attempts=body.quiz_attempts,
        last_accessed=timestamp,
        time_spent_seconds=body.time_spent_seconds,
    )
    return get_chapter_progress(chapter_id)
