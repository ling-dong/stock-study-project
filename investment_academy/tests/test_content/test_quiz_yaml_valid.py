"""校验所有测验 YAML 文件的格式正确性"""
import yaml
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def find_quiz_files():
    return list(CONTENT.glob("**/quiz.yaml"))


def _get_all_questions(data: dict) -> list[dict]:
    """从新旧两种 quiz.yaml 格式中提取所有题目"""
    questions = []
    # 新格式: {chapters: {p1_ch1: {questions: [...]}}}
    if "chapters" in data:
        for chapter_id, chapter_data in data["chapters"].items():
            for q in chapter_data.get("questions", []):
                q["_chapter"] = chapter_id
                questions.append(q)
    # 旧格式: {chapter: "...", questions: [...]}
    elif "questions" in data:
        questions = data["questions"]
    return questions


def test_all_quiz_files_parseable():
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{qf} 无法解析"
        questions = _get_all_questions(data)
        assert len(questions) > 0, f"{qf} 没有题目"
        for q in questions:
            assert "id" in q, f"{qf}: 问题缺少 id"
            assert "type" in q, f"{qf}: {q['id']} 缺少 type"
            assert "question" in q, f"{qf}: {q['id']} 缺少 question"
            assert "answer" in q, f"{qf}: {q['id']} 缺少 answer"


def test_all_quiz_questions_have_valid_types():
    valid_types = {"single_choice", "multi_choice", "true_false"}
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for q in _get_all_questions(data):
            assert q["type"] in valid_types, f"{qf}: {q['id']} 类型无效: {q['type']}"
            if q["type"] == "single_choice":
                assert isinstance(q["answer"], int), f"{qf}: {q['id']} answer应为int"
            if q["type"] == "multi_choice":
                assert isinstance(q["answer"], list), f"{qf}: {q['id']} answer应为list"
            if q["type"] == "true_false":
                assert isinstance(q["answer"], bool), f"{qf}: {q['id']} answer应为bool"


def test_each_chapter_has_5_questions():
    """验证每章恰好 5 道题"""
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if "chapters" in data:
            for chapter_id, chapter_data in data["chapters"].items():
                n = len(chapter_data.get("questions", []))
                assert n == 5, f"{qf}: {chapter_id} 有 {n} 题，期望 5 题"
