"""学习内容加载器 — 加载 Markdown 章节和 YAML 测验"""
from pathlib import Path
from typing import Optional
import yaml

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"


def list_phases() -> list[dict]:
    """列出所有知识轨道阶段"""
    kt = CONTENT_ROOT / "knowledge_track"
    if not kt.exists():
        return []
    phases = []
    for d in sorted(kt.iterdir()):
        if d.is_dir():
            chapters = sorted(d.glob("chapter_*.md"))
            has_quiz = (d / "quiz.yaml").exists()
            phases.append({
                "id": d.name,
                "chapter_count": len(chapters),
                "has_quiz": has_quiz,
            })
    return phases


def list_labs() -> list[dict]:
    """列出所有实践轨道实验室"""
    pt = CONTENT_ROOT / "practice_track"
    if not pt.exists():
        return []
    labs = []
    for d in sorted(pt.iterdir()):
        if d.is_dir():
            has_guide = (d / "lab_guide.md").exists()
            has_exercises = (d / "exercises.yaml").exists()
            labs.append({
                "id": d.name,
                "has_guide": has_guide,
                "has_exercises": has_exercises,
            })
    return labs


def load_chapter(phase_id: str, chapter_file: str) -> Optional[str]:
    """加载章节 Markdown 内容"""
    path = CONTENT_ROOT / "knowledge_track" / phase_id / chapter_file
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_quiz(phase_id: str) -> Optional[dict]:
    """加载测验配置"""
    path = CONTENT_ROOT / "knowledge_track" / phase_id / "quiz.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_lab_guide(lab_id: str) -> Optional[str]:
    """加载实验室指南"""
    path = CONTENT_ROOT / "practice_track" / lab_id / "lab_guide.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_lab_exercises(lab_id: str) -> Optional[dict]:
    """加载实验室练习"""
    path = CONTENT_ROOT / "practice_track" / lab_id / "exercises.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
