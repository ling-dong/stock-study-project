"""§5.2.3 回测记录模型"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class BacktestRecord(BaseModel):
    """回测记录表 backtest_record — §5.2.3 表2"""
    version_id: str = Field(..., max_length=32, description="系统版本标识（四元组）")
    record_id: int = Field(..., description="记录序号")
    symbol: str = Field(..., max_length=16, description="标的代码")
    entry_time: datetime = Field(..., description="入场时间戳")
    exit_time: Optional[datetime] = Field(default=None, description="出场时间戳")
    entry_price: Decimal = Field(..., max_digits=12, decimal_places=4)
    exit_price: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=4)
    pnl: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=4, description="毛收益")
    costs: Decimal = Field(..., max_digits=10, decimal_places=4, description="总交易成本")
    setup_type: str = Field(..., max_length=8, description="触发交易的Setup类型")
    position_size: Decimal = Field(..., max_digits=8, decimal_places=4, description="仓位比例")
    trigger_constraint: Optional[str] = Field(default=None, max_length=16, description="触发硬约束层级")

    @property
    def net_pnl(self) -> Optional[Decimal]:
        if self.pnl is None:
            return None
        return self.pnl - self.costs

    @property
    def is_win(self) -> Optional[bool]:
        net = self.net_pnl
        if net is None:
            return None
        return net > 0
