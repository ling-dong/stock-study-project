"""§5.1.3 市场状态模型"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MarketStateType(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


class RegimeType(str, Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"


class MarketState(BaseModel):
    """市场状态表 market_state — §5.1.3 表1"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="状态记录时间戳")
    timeframe: str = Field(..., max_length=8, description="时间框架")
    state: MarketStateType = Field(..., description="市场状态（bull/bear/neutral）")
    confidence: Decimal = Field(
        ..., ge=0, le=1, max_digits=4, decimal_places=3,
        description="状态置信度[0,1]，随持续时间递增"
    )
    duration: int = Field(..., ge=1, description="状态持续K线数")
    regime_classification: Optional[RegimeType] = Field(default=None, description="regime分类标签")

    @property
    def is_trending(self) -> bool:
        return self.state in (MarketStateType.BULL, MarketStateType.BEAR)

    @property
    def is_high_confidence(self) -> bool:
        return float(self.confidence) >= 0.7
