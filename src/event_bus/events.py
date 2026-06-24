"""§7.1.1 事件类型定义 — 四类核心事件"""
from datetime import datetime
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class EventType(str, Enum):
    BAR_CLOSE = "bar_close"
    FEATURE_COMPUTE = "feature_compute"
    STATE_TRANSITION = "state_transition"
    SETUP_DETECTED = "setup_detected"
    CONSENSUS_UPDATE = "consensus_update"
    PREDICTION_TRIGGER = "prediction_trigger"
    PREDICTION = "prediction"
    SENTIMENT_CACHED = "sentiment_cached"
    SIGNAL = "signal"


class EventHeader(BaseModel):
    """统一事件消息头 — §7.1.1"""
    trace_id: str = Field(default_factory=lambda: uuid4().hex[:16])
    event_id: str = Field(default_factory=lambda: uuid4().hex)
    parent_event_id: str = ""
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    version: str = "v1.0"
    source_service: str = ""
    data_version: str = "v1"


class BarCloseEvent(BaseModel):
    """K线闭合事件 — 事件流根节点"""
    header: EventHeader
    symbol: str
    timeframe: str
    bar_timestamp: datetime
    data_availability_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class FeatureComputeEvent(BaseModel):
    """特征计算事件 — BarFeatureSvc输出"""
    header: EventHeader
    symbol: str
    timeframe: str
    feature_name: str
    feature_value: float
    is_stale: bool = False
    decay_weight: float = 1.0


class StateTransitionEvent(BaseModel):
    """状态转移事件 — MarketStateSvc输出"""
    header: EventHeader
    symbol: str
    timeframe: str
    previous_state: str = ""
    new_state: str
    confidence: float
    duration: int


class SetupDetectedEvent(BaseModel):
    """Setup检测事件 — SetupRecogSvc输出"""
    header: EventHeader
    symbol: str
    timeframe: str
    setup_type: str
    status: str  # candidate/confirmed/invalidated
    quality_score: float
    maturity: int


class ConsensusUpdateEvent(BaseModel):
    """板块一致性事件 — ConsensusSvc输出"""
    header: EventHeader
    sector_id: str
    up_ratio: float
    momentum_median: float
    leader_corr: float = 0.0
    is_stale: bool = False


class PredictionEvent(BaseModel):
    """预测事件 — 模型服务输出"""
    header: EventHeader
    symbol: str
    direction_prob: float
    calibrated_prob: float
    raw_prob: float = 0.0
    confidence_level: str
    setup_type: str
    expected_value: float
    r_r_ratio: float


class SignalEvent(BaseModel):
    """最终交易信号事件 — §7.3.1"""
    header: EventHeader
    symbol: str
    setup_type: str
    direction: str
    raw_probability: float
    adjusted_probability: float
    risk_reward_ratio: float
    expected_return: float
    confidence_level: str
    deviation_analysis: str = ""
