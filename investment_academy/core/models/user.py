"""用户偏好与心理记录模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserPreferences:
    """用户偏好"""
    current_phase: str = "p1"
    preferred_timeframe: str = "day"
    sandbox_balance: float = 100000.0
    achievements: list = field(default_factory=list)
    risk_profile: str = "moderate"

    def to_dict(self) -> dict:
        return {
            "current_phase": self.current_phase,
            "preferred_timeframe": self.preferred_timeframe,
            "sandbox_balance": self.sandbox_balance,
            "achievements": self.achievements,
            "risk_profile": self.risk_profile,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UserPreferences":
        return cls(
            current_phase=d.get("current_phase", "p1"),
            preferred_timeframe=d.get("preferred_timeframe", "day"),
            sandbox_balance=float(d.get("sandbox_balance", 100000.0)),
            achievements=list(d.get("achievements", [])),
            risk_profile=d.get("risk_profile", "moderate"),
        )


@dataclass
class PsychologyCheckRecord:
    """心理自检记录"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scores: dict = field(default_factory=dict)
    overall_risk_level: str = "green"
    proceeded_to_trade: bool = False
    self_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "scores": self.scores,
            "overall_risk_level": self.overall_risk_level,
            "proceeded_to_trade": self.proceeded_to_trade,
            "self_notes": self.self_notes,
        }


@dataclass
class TradingJournalEntry:
    """交易日志"""
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    setup_type: str = ""
    entry_reason: str = ""
    exit_reason: str = ""
    pnl_pct: float = 0.0
    emotional_state: str = ""
    lesson_learned: str = ""
    mistake_flag: bool = False

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "setup_type": self.setup_type,
            "entry_reason": self.entry_reason,
            "exit_reason": self.exit_reason,
            "pnl_pct": self.pnl_pct,
            "emotional_state": self.emotional_state,
            "lesson_learned": self.lesson_learned,
            "mistake_flag": self.mistake_flag,
        }
