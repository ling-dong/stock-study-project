"""校验所有测验 YAML 文件的格式正确性"""
import yaml
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def find_quiz_files():
    return list(CONTENT.glob("**/quiz.yaml"))


def test_all_quiz_files_parseable():
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{qf} 无法解析"
        assert "questions" in data, f"{qf} 缺少 questions"
        for q in data["questions"]:
            assert "id" in q, f"{qf}: 问题缺少 id"
            assert "type" in q, f"{qf}: {q['id']} 缺少 type"
            assert "question" in q, f"{qf}: {q['id']} 缺少 question"
            assert "answer" in q, f"{qf}: {q['id']} 缺少 answer"


def test_all_quiz_questions_have_valid_types():
    valid_types = {"single_choice", "multi_choice", "true_false"}
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for q in data["questions"]:
            assert q["type"] in valid_types, f"{qf}: {q['id']} 类型无效: {q['type']}"
            if q["type"] == "single_choice":
                assert isinstance(q["answer"], int), f"{qf}: {q['id']} answer应为int"
            if q["type"] == "multi_choice":
                assert isinstance(q["answer"], list), f"{qf}: {q['id']} answer应为list"
            if q["type"] == "true_false":
                assert isinstance(q["answer"], bool), f"{qf}: {q['id']} answer应为bool"
