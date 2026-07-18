"""测试内容加载器"""
from core.engine.content_loader import (
    list_phases, list_labs, load_chapter, load_quiz, load_lab_guide
)


def test_list_phases():
    phases = list_phases()
    assert len(phases) > 0
    p1 = [p for p in phases if p["id"] == "p1_basics"]
    assert len(p1) == 1
    assert "chapter_count" in p1[0]


def test_load_chapter_exists():
    content = load_chapter("p1_basics", "chapter_01_stock_concept.md")
    assert content is not None
    assert "股票" in content
    assert "## 1.1" in content


def test_load_chapter_not_exists():
    content = load_chapter("nonexistent", "fake.md")
    assert content is None


def test_load_quiz():
    """不传 chapter_id 时返回 chapters 字典"""
    quiz = load_quiz("p1_basics")
    assert quiz is not None
    assert "chapters" in quiz
    assert "p1_ch1" in quiz["chapters"]
    ch1 = quiz["chapters"]["p1_ch1"]
    assert len(ch1["questions"]) == 5
    for q in ch1["questions"]:
        assert "id" in q
        assert "type" in q
        assert "question" in q
        assert "answer" in q
        assert "explanation" in q


def test_load_quiz_with_chapter_id():
    """传 chapter_id 时返回单章测验"""
    quiz = load_quiz("p1_basics", "p1_ch2")
    assert quiz is not None
    assert quiz["chapter"] == "p1_ch2"
    assert len(quiz["questions"]) == 5


def test_load_quiz_nonexistent():
    """不存在的阶段"""
    quiz = load_quiz("nonexistent")
    assert quiz is None


def test_list_labs():
    labs = list_labs()
    m1 = [l for l in labs if l["id"] == "m1_data_lab"]
    assert len(m1) == 1
