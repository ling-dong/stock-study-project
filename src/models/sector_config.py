"""§5.3.1 板块配置模型"""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ConstituentWeight(BaseModel):
    """成分股权重（含point-in-time历史权重）"""
    code: str = Field(..., max_length=16, description="成分股代码")
    name: str = Field(..., description="成分股名称")
    weight: Decimal = Field(..., ge=0, le=1, max_digits=6, decimal_places=4)
    effective_from: date = Field(..., description="生效起始日期")
    effective_to: Optional[date] = Field(default=None, description="生效截止日期")


class SectorConfig(BaseModel):
    """板块配置表 sector_config — §5.3.1"""
    sector_id: str = Field(..., max_length=16, description="申万行业代码")
    name: str = Field(..., description="板块名称")
    etf_code: str = Field(..., max_length=16, description="代理ETF代码")
    index_code: str = Field(..., max_length=16, description="板块指数代码")
    constituents: list[ConstituentWeight] = Field(default_factory=list)
    timeframes: list[str] = Field(
        default_factory=lambda: ["5min", "15min", "60min", "day"]
    )
    analysis_level: str = Field(default="basic")
    related_sectors: list[str] = Field(default_factory=list)

    def get_constituents_at(self, target_date: date) -> list[ConstituentWeight]:
        """获取指定日期的point-in-time成分股权重"""
        return [
            c for c in self.constituents
            if c.effective_from <= target_date
            and (c.effective_to is None or c.effective_to > target_date)
        ]
