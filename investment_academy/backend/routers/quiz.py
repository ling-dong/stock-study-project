"""测验系统 — 评分 + 持久化"""
from fastapi import APIRouter, HTTPException
from interactive.content_loader import load_quiz
from models.quiz import QuizQuestion
from db.repository import save_quiz_result, save_chapter_progress, get_chapter_progress
from backend.schemas import QuizSubmitIn, QuizSubmitOut
from datetime import datetime

router = APIRouter(prefix="/api/quiz", tags=["测验系统"])


def _score_quiz(questions: list[dict], answers: dict) -> tuple[int, int, list[dict]]:
    """纯函数：评分并生成解析"""
    correct = 0
    explanations = []
    for q_raw in questions:
        q = QuizQuestion.from_dict(q_raw)
        user_ans = answers.get(q.id)
        is_correct = False

        if user_ans is not None:
            if isinstance(q.answer, list) and isinstance(user_ans, list):
                is_correct = set(user_ans) == set(q.answer)
            else:
                is_correct = user_ans == q.answer

        if is_correct:
            correct += 1

        explanations.append({
            "question_id": q.id,
            "correct_answer": q.answer,
            "explanation": q.explanation,
            "user_correct": is_correct,
        })

    return correct, len(questions), explanations


def _score_to_label(score: float) -> str:
    """分数转标签"""
    if score >= 0.8:
        return "优秀！"
    elif score >= 0.6:
        return "通过，继续加油！"
    else:
        return "建议重新学习本章"


@router.post("/submit", response_model=QuizSubmitOut)
def submit_quiz(body: QuizSubmitIn):
    """提交测验答案，返回评分 + 解析，并持久化结果"""
    quiz_data = load_quiz(body.phase_id)
    if quiz_data is None:
        raise HTTPException(status_code=404, detail=f"测验不存在: {body.phase_id}")

    questions = quiz_data.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="该测验没有题目")

    correct_count, total, explanations = _score_quiz(questions, body.answers)
    score = correct_count / total if total > 0 else 0.0
    passed = score >= 0.6
    timestamp = datetime.now().isoformat()

    # 持久化测验结果
    save_quiz_result(
        chapter_id=body.chapter_id,
        total_questions=total,
        correct_count=correct_count,
        score=score,
        answers=body.answers,
        timestamp=timestamp,
    )

    # 更新章节进度
    existing = get_chapter_progress(body.chapter_id)
    attempts = (existing.get("quiz_attempts", 0) + 1) if existing else 1
    save_chapter_progress(
        chapter_id=body.chapter_id,
        completed=passed,
        quiz_score=score,
        quiz_attempts=attempts,
        last_accessed=timestamp,
    )

    return {
        "score": score,
        "correct_count": correct_count,
        "total": total,
        "passed": passed,
        "explanations": explanations,
    }
