"""测试内容加载器"""
from interactive.content_loader import (
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
    quiz = load_quiz("p1_basics")
    assert quiz is not None
    assert "questions" in quiz
    assert len(quiz["questions"]) == 5
    for q in quiz["questions"]:
        assert "id" in q
        assert "type" in q
        assert "question" in q
        assert "answer" in q
        assert "explanation" in q


def test_list_labs():
    labs = list_labs()
    m1 = [l for l in labs if l["id"] == "m1_data_lab"]
    assert len(m1) == 1
