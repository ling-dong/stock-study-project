"""内容系统 — 章节、测验、实验室"""
from fastapi import APIRouter, HTTPException
from core.engine.content_loader import (
    list_phases, list_labs, list_chapters, load_chapter, load_quiz, load_lab_guide, load_lab_exercises,
)
from core.utils.path_utils import validate_content_id, validate_chapter_filename
from backend.schemas import ChapterContentOut, QuizContentOut, LabContentOut

router = APIRouter(prefix="/api/content", tags=["内容系统"])


@router.get("/phases")
def get_phases():
    """知识轨道阶段列表"""
    return list_phases()


@router.get("/chapters/{phase_id}")
def get_chapters(phase_id: str):
    """某阶段的章节列表"""
    if not validate_content_id(phase_id):
        raise HTTPException(status_code=400, detail="非法的阶段 ID")
    return list_chapters(phase_id)


@router.get("/labs")
def get_labs():
    """实践实验室列表"""
    return list_labs()


@router.get("/chapter/{phase_id}/{filename}")
def get_chapter(phase_id: str, filename: str):
    """加载章节 Markdown 内容"""
    if not validate_content_id(phase_id) or not validate_chapter_filename(filename):
        raise HTTPException(status_code=400, detail="非法的阶段 ID 或文件名")
    content = load_chapter(phase_id, filename)
    if content is None:
        raise HTTPException(status_code=404, detail=f"章节不存在: {phase_id}/{filename}")
    return {"content": content}


@router.get("/quiz/{phase_id}")
def get_quiz(phase_id: str, chapter_id: str = None):
    """加载测验配置"""
    if not validate_content_id(phase_id) or (chapter_id and not validate_content_id(chapter_id)):
        raise HTTPException(status_code=400, detail="非法的阶段 ID 或章节 ID")
    data = load_quiz(phase_id, chapter_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"测验不存在: {phase_id}")
    return data


@router.get("/lab/{lab_id}")
def get_lab(lab_id: str):
    """加载实验室内容"""
    if not validate_content_id(lab_id):
        raise HTTPException(status_code=400, detail="非法的实验室 ID")
    guide = load_lab_guide(lab_id)
    exercises = load_lab_exercises(lab_id)
    if guide is None and exercises is None:
        raise HTTPException(status_code=404, detail=f"实验室不存在: {lab_id}")
    return {"guide": guide, "exercises": exercises}
