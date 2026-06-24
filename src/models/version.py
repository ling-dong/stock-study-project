"""§5.3.2 系统版本模型

system_version 表：回测可复现性的基石。
四子版本：rules_version, model_version, features_version, data_version。
"""
from datetime import datetime
from pydantic import BaseModel, Field


class SystemVersion(BaseModel):
    """系统版本表 system_version — §5.3.2"""
    version_id: str = Field(..., max_length=32, description="系统版本标识")
    rules_version: str = Field(..., description="规则引擎版本")
    model_version: str = Field(..., description="ML模型版本（训练日期+Git Commit哈希）")
    features_version: str = Field(..., description="特征计算版本")
    data_version: str = Field(..., description="数据批次版本")
    calibration_params: dict = Field(default_factory=dict, description="Isotonic Regression断点与映射值")
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=False)

    @property
    def full_identifier(self) -> str:
        return (
            f"{self.version_id}="
            f"{{rules_{self.rules_version},"
            f"model_{self.model_version},"
            f"features_{self.features_version},"
            f"data_{self.data_version}}}"
        )
