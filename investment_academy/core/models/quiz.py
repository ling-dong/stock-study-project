"""测验数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class QuizQuestion:
    """单道测验题"""
    id: str
    type: str            # "single_choice" | "multi_choice" | "true_false"
    question: str
    options: list
    answer: object       # single_choice: int index; multi_choice: list[int]; true_false: bool
    explanation: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "QuizQuestion":
        return cls(
            id=d["id"],
            type=d["type"],
            question=d["question"],
            options=list(d.get("options", [])),
            answer=d["answer"],
            explanation=d.get("explanation", ""),
        )


@dataclass
class QuizResult:
    """单次测验结果"""
    chapter_id: str
    total_questions: int
    correct_count: int
    score: float           # 0.0 - 1.0
    answers: dict          # {question_id: user_answer}
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def passed(self) -> bool:
        """>=60% 为通过"""
        return self.score >= 0.6

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": self.score,
            "answers": self.answers,
            "timestamp": self.timestamp,
        }
