"""§5.2.2 预测输出模型"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class PredictionOutput(BaseModel):
    """预测输出表 prediction_output — §5.2.2 表2"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="预测时间戳")
    direction_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="上涨方向概率（Isotonic校准后）[0,1]"
    )
    target_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="目标达成概率[0,1]"
    )
    stop_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="止损触发概率[0,1]"
    )
    r_r_ratio: Decimal = Field(
        ..., max_digits=6, decimal_places=3,
        description="风险回报比 = target_dist/stop_dist"
    )
    expected_value: Decimal = Field(
        ..., max_digits=8, decimal_places=6,
        description="期望收益率（含交易成本的三态期望）"
    )
    setup_type: str = Field(..., max_length=8, description="触发预测的Setup类型")
    model_version: str = Field(..., max_length=32, description="产出预测的模型版本（审计）")
    raw_probability: Optional[Decimal] = Field(
        default=None, ge=0, le=1, max_digits=5, decimal_places=4,
        description="校准前原始概率"
    )
    confidence_level: str = Field(default="medium", description="置信度等级")
