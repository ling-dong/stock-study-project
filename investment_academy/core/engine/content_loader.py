"""学习内容加载器 — 加载 Markdown 章节和 YAML 测验"""
from pathlib import Path
from typing import Optional
import yaml

CONTENT_ROOT = Path(__file__).resolve().parent.parent.parent / "content"


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


def list_chapters(phase_id: str) -> list[dict]:
    """列出某阶段的所有章节（文件 + ID + 标题）"""
    phase_dir = CONTENT_ROOT / "knowledge_track" / phase_id
    if not phase_dir.exists():
        return []
    md_files = sorted(phase_dir.glob("chapter_*.md"))
    chapters = []
    for f in md_files:
        ch = {"file": f.name}
        # 读取 Markdown 第一行作为标题
        try:
            first_line = f.read_text(encoding="utf-8").split("\n")[0]
            ch["title"] = first_line.lstrip("# ").strip()
        except Exception:
            ch["title"] = f.stem
        chapters.append(ch)
    # 从 quiz.yaml 获取章节 ID
    quiz = load_quiz(phase_id)
    if quiz and "chapters" in quiz:
        ch_ids = list(quiz["chapters"].keys())
        for i, ch in enumerate(chapters):
            if i < len(ch_ids):
                ch["id"] = ch_ids[i]
    return chapters


def load_chapter(phase_id: str, chapter_file: str) -> Optional[str]:
    """加载章节 Markdown 内容"""
    path = CONTENT_ROOT / "knowledge_track" / phase_id / chapter_file
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_quiz(phase_id: str, chapter_id: str = None) -> Optional[dict]:
    """加载测验配置

    Args:
        phase_id: 阶段 ID，如 'p1_basics'
        chapter_id: 章节 ID，如 'p1_ch1'。不传则返回全部章节的测验
    """
    path = CONTENT_ROOT / "knowledge_track" / phase_id / "quiz.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if chapter_id and data:
        chapters = data.get("chapters", {})
        chapter_data = chapters.get(chapter_id)
        if chapter_data:
            return {"chapter": chapter_id, "questions": chapter_data.get("questions", [])}
        return None

    return data


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
