"""§5.1.2 特征数据模型

feature_vector 表：存储四个微服务的计算输出。
每个特征标注 computation_time 与 dependencies_version。
future_function_violation 构成未来函数防护的最后一道关卡。
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FeatureVector(BaseModel):
    """特征数据表 feature_vector — §5.1.2 表1

    Model is frozen (immutable) to guarantee reproducibility.
    """
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="特征对应K线时间戳")
    timeframe: str = Field(..., max_length=8, description="时间框架")
    feature_name: str = Field(..., max_length=32, description="特征名称，如 body_ratio")
    feature_value: float = Field(..., description="基于lagged价格计算的特征值")
    computation_time: datetime = Field(..., description="特征计算完成时间（审计追溯）")
    dependencies_version: str = Field(..., max_length=64, description="依赖数据版本摘要")
    future_function_violation: bool = Field(default=False, description="未来函数违规标记")
