"""Pydantic 请求/响应模型"""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Content ──────────────────────────────────────────────

class PhaseOut(BaseModel):
    id: str
    chapter_count: int
    has_quiz: bool

class LabOut(BaseModel):
    id: str
    has_guide: bool
    has_exercises: bool

class ChapterContentOut(BaseModel):
    content: str

class QuizContentOut(BaseModel):
    chapter: str
    questions: list[dict]

class LabContentOut(BaseModel):
    guide: Optional[str] = None
    exercises: Optional[dict] = None


# ── Quiz ─────────────────────────────────────────────────

class QuizSubmitIn(BaseModel):
    phase_id: str
    chapter_id: str
    answers: dict[str, Any]  # {question_id: user_answer}

class QuizExplanation(BaseModel):
    question_id: str
    correct_answer: Any
    explanation: str
    user_correct: bool

class QuizSubmitOut(BaseModel):
    score: float
    correct_count: int
    total: int
    passed: bool
    explanations: list[dict]


# ── Progress ─────────────────────────────────────────────

class ChapterProgressOut(BaseModel):
    chapter_id: str
    completed: bool = False
    quiz_score: float = 0.0
    quiz_attempts: int = 0
    last_accessed: Optional[str] = None
    time_spent_seconds: int = 0

class ChapterProgressUpdateIn(BaseModel):
    completed: bool = False
    quiz_score: float = 0.0
    quiz_attempts: int = 0
    time_spent_seconds: int = 0


# ── Market ───────────────────────────────────────────────

class ETFInfo(BaseModel):
    code: str
    market: str
    file: str
    has_5min: bool

class ETFMetadata(BaseModel):
    code: str
    market: str
    rows: int
    start_date: str
    end_date: str

class ETFName(BaseModel):
    code: str
    display_name: str

class OHLCVBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class OHLCVResponse(BaseModel):
    code: str
    timeframe: str
    bars: list[dict]


# ── Sandbox ──────────────────────────────────────────────

class SandboxInitIn(BaseModel):
    etf_code: str
    timeframe: str = "day"
    initial_cash: float = 100000.0
    start_date: Optional[str] = None

class SandboxInitOut(BaseModel):
    session_id: str
    total_bars: int = 0

class SandboxStateOut(BaseModel):
    session_id: str
    cash: float
    shares: int
    cost_basis: float
    index: int
    total_bars: int
    is_done: bool

class SandboxBuyIn(BaseModel):
    shares: int
    reason: str = ""

class SandboxSellIn(BaseModel):
    shares: int = 0      # 0 = 全部卖出
    reason: str = ""

class SandboxTradeOut(BaseModel):
    date: str
    action: str
    price: float
    shares: int
    amount: float
    reason: str
    cost: float

class SandboxPortfolioOut(BaseModel):
    cash: float
    shares: int
    price: float
    value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    cost_basis: float


# ── User ─────────────────────────────────────────────────

class UserPreferencesIn(BaseModel):
    current_phase: str = "p1"
    preferred_timeframe: str = "day"
    sandbox_balance: float = 100000.0
    achievements: list[str] = []
    risk_profile: str = "moderate"

class UserPreferencesOut(BaseModel):
    current_phase: str
    preferred_timeframe: str
    sandbox_balance: float
    achievements: list
    risk_profile: str

class PsychologyCheckIn(BaseModel):
    scores: dict = {}
    overall_risk_level: str = "green"
    proceeded_to_trade: bool = False
    self_notes: str = ""

class TradingJournalIn(BaseModel):
    date: str = ""
    setup_type: str = ""
    entry_reason: str = ""
    exit_reason: str = ""
    pnl_pct: float = 0.0
    emotional_state: str = ""
    lesson_learned: str = ""
    mistake_flag: bool = False
