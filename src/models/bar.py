"""§5.1.1 K线数据模型"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class TimeFrame(str, Enum):
    M5 = "5min"
    M15 = "15min"
    M60 = "60min"
    DAY = "day"


class DataSource(str, Enum):
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    LOCAL = "local"


class BarOHLCV(BaseModel):
    """K线数据表 bar_ohlcv — §5.1.1 表1

    Constraint: high >= max(open, close)
    Constraint: low <= min(open, close)
    Constraint: data_availability_time >= timestamp
    """
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="K线结束时间戳")
    timeframe: TimeFrame = Field(..., description="时间框架")
    open: Decimal = Field(..., max_digits=12, decimal_places=4)
    high: Decimal = Field(..., max_digits=12, decimal_places=4)
    low: Decimal = Field(..., max_digits=12, decimal_places=4)
    close: Decimal = Field(..., max_digits=12, decimal_places=4)
    volume: int = Field(..., ge=0, description="成交量（手）")
    data_availability_time: datetime = Field(..., description="数据可用时间戳")
    source: DataSource = Field(..., description="数据来源")
    stale: bool = Field(default=False, description="数据缺失标记")
    data_version: int = Field(default=1, ge=1, description="数据版本号")

    @model_validator(mode="after")
    def _validate_ohlc(self) -> "BarOHLCV":
        if self.high < max(self.open, self.close):
            raise ValueError(f"high({self.high}) must be >= max(open,close)")
        if self.low > min(self.open, self.close):
            raise ValueError(f"low({self.low}) must be <= min(open,close)")
        if self.data_availability_time < self.timestamp:
            raise ValueError(
                f"data_availability_time({self.data_availability_time}) "
                f"must be >= timestamp({self.timestamp})"
            )
        return self


class BarAdjustment(BaseModel):
    """复权因子表 bar_adjustment"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    date: datetime = Field(..., description="除权日期")
    factor: Decimal = Field(..., max_digits=12, decimal_places=8, description="复权因子")
    description: Optional[str] = None
