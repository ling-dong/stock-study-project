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


# ── SPAS 预测系统 ─────────────────────────────────────────

class SPASAnalysisIn(BaseModel):
    """SPAS 分析请求 — 用户从同花顺抄入的指标值 + 偏好 + 心理问卷"""
    # DMI 组
    adx: float = Field(..., ge=0, le=100, description="ADX 趋势强度")
    plus_di: float = Field(..., description="+DI 上升方向线")
    minus_di: float = Field(..., description="-DI 下降方向线")
    atr: float = Field(..., gt=0, description="ATR(14) 平均真实波幅")
    # ASI 组
    asi_value: float = Field(..., description="ASI 振动升降指数当前值")
    asi_direction: str = Field(..., description="ASI 方向: up / down / flat")
    # MACD 组
    dif: float = Field(..., description="MACD DIF 快线")
    dea: float = Field(..., description="MACD DEA 慢线")
    macd_bar: str = Field(..., description="MACD 柱状态: red_increasing / red_decreasing / green_increasing / green_decreasing")
    # 热度组
    rsi: float = Field(..., ge=0, le=100, description="RSI(14)")
    wr: float = Field(..., ge=0, le=100, description="WR(14) 威廉指标 — 同花顺格式 0~100")
    # 量价组
    volume_ratio: float = Field(..., description="当日量比 (今日成交量/5日均量)")
    turnover_rate: float = Field(..., ge=0, description="换手率 %")
    # OBV
    obv_direction: str = Field(..., description="OBV 方向: up / down / flat")
    # 大盘环境
    market_trend: str = Field(..., description="大盘趋势: bull / range / bear")
    market_adx: float = Field(..., ge=0, le=100, description="大盘 ADX")
    # 用户偏好
    current_price: Optional[float] = Field(default=None, description="实时价格 — 从同花顺填入，不填则用数据最新收盘价")
    rr_ratio: float = Field(default=2.0, ge=1.0, le=5.0, description="风险回报比")
    max_loss_pct: float = Field(default=5.0, ge=1.0, le=15.0, description="最大可接受亏损 %")
    # 心理问卷（10题，原始选项索引，每题选项数可不同）
    psychology_answers: list[int] = Field(..., min_length=10, max_length=10, description="心理问卷10题原始答案索引")
    psychology_max_score: Optional[int] = Field(default=50, ge=10, le=200, description="心理问卷原始总分上限，用于动态缩放")


class SPASProbFactor(BaseModel):
    """单个概率因子的贡献"""
    factor: str          # 因子名称
    contribution: float  # 贡献值（如 +0.10 表示 +10%）
    detail: str = ""     # 因子详情


class SPASProbabilityOut(BaseModel):
    """概率分析结果"""
    direction: str              # bullish / bearish / neutral
    probability: float          # 最终概率 [0.25, 0.85]
    base_probability: float     # 基准概率 0.50
    factors: list[SPASProbFactor]  # 各因子贡献分解


class SPASPositionOut(BaseModel):
    """仓位建议"""
    kelly_f_star: float         # Kelly 公式 f*
    kelly_fractional: float     # 1/4 fractional Kelly
    psychology_score: int       # 心理问卷总分 (0-30)
    psychology_factor: float    # 心理调整因子 [0.5, 1.0]
    psychology_level: str       # 心理等级
    psychology_warnings: list[str]  # 心理警告
    suggested_position_pct: float   # 最终建议仓位 %


class SPASRiskOut(BaseModel):
    """止盈止损建议"""
    current_price: float
    atr: float
    atr_multiplier: int = 2
    stop_loss_price: float          # 止损价
    stop_loss_pct: float            # 止损幅度 %
    take_profit_price: float        # 止盈价
    take_profit_pct: float          # 止盈幅度 %
    rr_ratio: float                 # 使用的 R:R 比
    stop_capped_by_max_loss: bool   # 止损是否被最大亏损限制
    tp_capped: bool = False         # 止盈是否被安全上限限制
    atr_warning: bool = False       # ATR 值是否异常（>当前价20%）


class SPASTechnicalOut(BaseModel):
    """系统自动计算的技术指标"""
    current_price: float
    ema: dict[str, float]           # ema5, ema10, ema20, ema60
    ema_slopes: dict[str, float]    # 各 EMA 斜率
    ma_alignment: str               # BULL / BEAR / NEUTRAL
    kline_features: dict[str, float]  # body_ratio, close_position, upper_shadow, lower_shadow
    kline_pattern: str              # bullish / bearish / neutral


class SPASAnalysisOut(BaseModel):
    """SPAS 完整分析响应"""
    symbol: str
    display_name: str
    timestamp: str
    probability: SPASProbabilityOut
    position: SPASPositionOut
    risk: SPASRiskOut
    technical: SPASTechnicalOut


class SPASHistoryItem(BaseModel):
    """历史记录列表项"""
    id: int
    etf_code: str
    etf_name: str
    created_at: str
    probability: float
    direction: str
    position_pct: float
    stop_loss: float
    take_profit: float
    psychology_score: int
    psychology_level: str


class SPASHistoryDetail(BaseModel):
    """历史记录详情（含完整输入/输出）"""
    id: int
    etf_code: str
    etf_name: str
    created_at: str
    probability: float
    direction: str
    position_pct: float
    stop_loss: float
    take_profit: float
    psychology_score: int
    psychology_level: str
    inputs: dict
    result: dict
