"""学习进度数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChapterProgress:
    """章节学习进度"""
    chapter_id: str              # e.g. "p1_ch1"
    completed: bool = False
    quiz_score: float = 0.0      # 0.0 - 1.0
    quiz_attempts: int = 0
    last_accessed: Optional[str] = None  # ISO 8601
    time_spent_seconds: int = 0

    def mark_completed(self, quiz_score: float = 0.0) -> None:
        self.completed = True
        self.quiz_score = quiz_score
        self.quiz_attempts += 1
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "completed": self.completed,
            "quiz_score": self.quiz_score,
            "quiz_attempts": self.quiz_attempts,
            "last_accessed": self.last_accessed,
            "time_spent_seconds": self.time_spent_seconds,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChapterProgress":
        return cls(
            chapter_id=d["chapter_id"],
            completed=bool(d.get("completed", False)),
            quiz_score=float(d.get("quiz_score", 0.0)),
            quiz_attempts=int(d.get("quiz_attempts", 0)),
            last_accessed=d.get("last_accessed"),
            time_spent_seconds=int(d.get("time_spent_seconds", 0)),
        )


@dataclass
class LabProgress:
    """实验室进度"""
    lab_id: str                  # e.g. "m1"
    completed: bool = False
    exercises_done: list = field(default_factory=list)
    last_accessed: Optional[str] = None

    def mark_exercise_done(self, exercise_id: str) -> None:
        if exercise_id not in self.exercises_done:
            self.exercises_done.append(exercise_id)
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "lab_id": self.lab_id,
            "completed": self.completed,
            "exercises_done": self.exercises_done,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LabProgress":
        return cls(
            lab_id=d["lab_id"],
            completed=bool(d.get("completed", False)),
            exercises_done=list(d.get("exercises_done", [])),
            last_accessed=d.get("last_accessed"),
        )
