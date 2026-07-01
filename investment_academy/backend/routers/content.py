"""内容系统 — 章节、测验、实验室"""
from fastapi import APIRouter, HTTPException
from interactive.content_loader import (
    list_phases, list_labs, load_chapter, load_quiz, load_lab_guide, load_lab_exercises,
)
from backend.schemas import ChapterContentOut, QuizContentOut, LabContentOut

router = APIRouter(prefix="/api/content", tags=["内容系统"])


@router.get("/phases")
def get_phases():
    """知识轨道阶段列表"""
    return list_phases()


@router.get("/labs")
def get_labs():
    """实践实验室列表"""
    return list_labs()


@router.get("/chapter/{phase_id}/{filename}")
def get_chapter(phase_id: str, filename: str):
    """加载章节 Markdown 内容"""
    content = load_chapter(phase_id, filename)
    if content is None:
        raise HTTPException(status_code=404, detail=f"章节不存在: {phase_id}/{filename}")
    return {"content": content}


@router.get("/quiz/{phase_id}")
def get_quiz(phase_id: str, chapter_id: str = None):
    """加载测验配置"""
    data = load_quiz(phase_id, chapter_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"测验不存在: {phase_id}")
    return data


@router.get("/lab/{lab_id}")
def get_lab(lab_id: str):
    """加载实验室内容"""
    guide = load_lab_guide(lab_id)
    exercises = load_lab_exercises(lab_id)
    if guide is None and exercises is None:
        raise HTTPException(status_code=404, detail=f"实验室不存在: {lab_id}")
    return {"guide": guide, "exercises": exercises}
