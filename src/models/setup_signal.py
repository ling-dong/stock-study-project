"""§5.2.1 Setup信号模型

setup_signal 表：H2/L2/FB三种Setup类型的候选态与确认态记录。
candidate_vs_confirmed 字段是数据泄漏防护的关键机制。
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class SetupType(str, Enum):
    H2 = "H2"
    L2 = "L2"
    FB = "FB"


class SetupStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    INVALIDATED = "invalidated"


class SetupSignal(BaseModel):
    """Setup信号表 setup_signal — §5.2.1 表2"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="信号时间戳")
    setup_type: SetupType = Field(..., description="Setup类型（H2/L2/FB）")
    candidate_vs_confirmed: SetupStatus = Field(
        ..., description="候选态/确认态/失效态"
    )
    quality_score: Decimal = Field(
        ..., ge=0, le=1, max_digits=4, decimal_places=3,
        description="结构质量评分[0,1]"
    )
    maturity: int = Field(..., ge=0, description="成熟度（从候选态起的K线数）")
    detection_bar_index: int = Field(..., description="检测Bar序号（Walk-Forward时序对齐）")

    @property
    def is_confirmed(self) -> bool:
        return self.candidate_vs_confirmed == SetupStatus.CONFIRMED

    @property
    def is_high_quality(self) -> bool:
        return float(self.quality_score) >= 0.7
