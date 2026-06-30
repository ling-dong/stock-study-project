"""交易沙盒引擎 — 纯逻辑，无 UI 依赖"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class Trade:
    """单笔交易记录"""
    date: str
    action: str        # "buy" | "sell"
    price: float
    shares: int
    amount: float      # price * shares
    reason: str = ""
    cost: float = 0.0  # 交易成本


@dataclass
class SandboxState:
    """沙盒状态"""
    cash: float = 100000.0
    shares: int = 0
    cost_basis: float = 0.0      # 每股成本
    total_cost: float = 0.0       # 总成本（含交易费）
    trades: list = field(default_factory=list)
    current_index: int = 0
    total_bars: int = 0


@dataclass
class PerformanceReport:
    """绩效报告"""
    initial_cash: float
    final_cash: float
    final_shares: int
    final_price: float
    total_value: float            # cash + shares * price
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown_pct: float
    total_costs: float
    trades: list


class SandboxEngine:
    """交易沙盒引擎"""

    # A 股交易参数
    STAMP_DUTY = 0.001       # 印花税（卖时收取）
    COMMISSION = 0.000025    # 佣金 0.25bps
    MIN_COMMISSION = 5.0     # 最低佣金 5元
    SLIPPAGE = 0.0001        # 滑点 1bp
    T_PLUS_1 = True          # T+1 制度
    PRICE_LIMIT = 0.10       # 涨跌停 10%

    def __init__(self, df: pd.DataFrame, initial_cash: float = 100000.0):
        """初始化沙盒

        Args:
            df: DataFrame with columns [trade_date, open, high, low, close, volume]
            initial_cash: 初始资金
        """
        required_cols = ["trade_date", "open", "high", "low", "close"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要列: {col}")

        self.df = df.sort_values("trade_date").reset_index(drop=True)
        self.state = SandboxState(
            cash=initial_cash,
            total_bars=len(df),
        )
        self._last_buy_date: Optional[str] = None

    @property
    def current_bar(self) -> dict:
        """获取当前 K 线数据"""
        if self.state.current_index >= len(self.df):
            return None
        row = self.df.iloc[self.state.current_index]
        return {
            "date": str(row["trade_date"])[:10],
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row.get("volume", 0)),
            "index": self.state.current_index,
            "is_last": self.state.current_index >= len(self.df) - 1,
        }

    @property
    def is_done(self) -> bool:
        """是否已走完所有数据"""
        return self.state.current_index >= len(self.df)

    def advance(self) -> Optional[dict]:
        """前进到下一天，返回新的 bar 或 None"""
        self.state.current_index += 1
        if self.is_done:
            return None
        return self.current_bar

    def can_buy(self) -> tuple[bool, str]:
        """检查是否可以买入"""
        if self.is_done:
            return False, "回测已结束"

        bar = self.current_bar
        price = bar["close"]

        # 检查 T+1
        if self.T_PLUS_1 and self._last_buy_date == bar["date"]:
            return False, "T+1 制度：当日买入的股票次日才能卖出"

        # 检查资金
        shares = self._calc_max_shares(price)
        if shares <= 0:
            return False, f"资金不足（可用: ¥{self.state.cash:,.0f}）"

        return True, f"最多可买 {shares} 股"

    def buy(self, shares: int, reason: str = "") -> Optional[Trade]:
        """买入股票

        Args:
            shares: 买入股数（必须是100的整数倍）
            reason: 买入理由
        """
        can, msg = self.can_buy()
        if not can:
            return None

        if shares <= 0:
            return None

        bar = self.current_bar
        price = bar["close"] * (1 + self.SLIPPAGE)
        amount = price * shares
        cost = self._calc_cost(amount, is_buy=True)
        total = amount + cost

        if total > self.state.cash:
            return None

        # 执行买入
        self.state.cash -= total
        old_total_cost = self.state.total_cost
        self.state.total_cost += total
        self.state.cost_basis = (
            (self.state.cost_basis * self.state.shares + total) / (self.state.shares + shares)
            if self.state.shares + shares > 0 else 0
        )
        self.state.shares += shares

        trade = Trade(
            date=bar["date"],
            action="buy",
            price=price,
            shares=shares,
            amount=amount,
            reason=reason,
            cost=cost,
        )
        self.state.trades.append(trade)
        self._last_buy_date = bar["date"]
        return trade

    def can_sell(self) -> tuple[bool, str]:
        """检查是否可以卖出"""
        if self.is_done:
            return False, "回测已结束"
        if self.state.shares <= 0:
            return False, "没有持仓"
        return True, f"可卖出 {self.state.shares} 股"

    def sell(self, shares: int, reason: str = "") -> Optional[Trade]:
        """卖出股票"""
        can, msg = self.can_sell()
        if not can:
            return None

        if shares <= 0 or shares > self.state.shares:
            shares = self.state.shares  # 全部卖出

        bar = self.current_bar
        price = bar["close"] * (1 - self.SLIPPAGE)
        amount = price * shares
        cost = self._calc_cost(amount, is_buy=False)
        net_amount = amount - cost

        self.state.cash += net_amount
        self.state.shares -= shares
        if self.state.shares == 0:
            self.state.cost_basis = 0.0
            self.state.total_cost = 0.0

        trade = Trade(
            date=bar["date"],
            action="sell",
            price=price,
            shares=shares,
            amount=amount,
            reason=reason,
            cost=cost,
        )
        self.state.trades.append(trade)
        return trade

    def get_portfolio_value(self) -> float:
        """当前总资产"""
        if self.is_done:
            return self.state.cash
        bar = self.current_bar
        return self.state.cash + self.state.shares * bar["close"]

    def get_unrealized_pnl(self) -> float:
        """未实现盈亏"""
        if self.state.shares == 0:
            return 0.0
        bar = self.current_bar
        current_value = self.state.shares * bar["close"]
        return current_value - self.state.total_cost

    def get_unrealized_pnl_pct(self) -> float:
        """未实现盈亏百分比"""
        if self.state.total_cost == 0:
            return 0.0
        return self.get_unrealized_pnl() / self.state.total_cost * 100

    def get_current_cost_basis(self) -> float:
        """当前持仓成本"""
        return self.state.cost_basis

    def get_performance(self) -> PerformanceReport:
        """获取完整绩效报告"""
        final_price = float(self.df.iloc[-1]["close"])
        total_value = self.state.cash + self.state.shares * final_price

        # 分析已完成的买卖对
        completed_trades = self._get_completed_trades()
        winning = sum(1 for t in completed_trades if t["pnl"] > 0)
        losing = sum(1 for t in completed_trades if t["pnl"] < 0)
        total_completed = len(completed_trades)

        total_costs = sum(t.cost for t in self.state.trades)

        return PerformanceReport(
            initial_cash=100000.0,
            final_cash=self.state.cash,
            final_shares=self.state.shares,
            final_price=final_price,
            total_value=total_value,
            total_return_pct=(total_value - 100000.0) / 100000.0 * 100,
            total_trades=len(self.state.trades),
            winning_trades=winning,
            losing_trades=losing,
            win_rate=winning / total_completed if total_completed > 0 else 0.0,
            max_drawdown_pct=self._calc_max_drawdown(),
            total_costs=total_costs,
            trades=self.state.trades,
        )

    def get_equity_curve(self) -> pd.DataFrame:
        """获取权益曲线（用于绘图）"""
        records = []
        cash = 100000.0
        shares = 0

        trade_idx = 0
        trades = self.state.trades

        for i, row in self.df.iterrows():
            close = float(row["close"])

            # 应用交易
            while trade_idx < len(trades) and trades[trade_idx].date <= str(row["trade_date"])[:10]:
                t = trades[trade_idx]
                if t.action == "buy":
                    cash -= (t.amount + t.cost)
                    shares += t.shares
                else:
                    cash += (t.amount - t.cost)
                    shares -= t.shares
                trade_idx += 1

            value = cash + shares * close
            records.append({
                "date": str(row["trade_date"])[:10],
                "value": value,
                "cash": cash,
                "shares": shares,
                "price": close,
            })

        return pd.DataFrame(records)

    def _calc_cost(self, amount: float, is_buy: bool) -> float:
        """计算交易成本"""
        commission = max(amount * self.COMMISSION, self.MIN_COMMISSION)
        stamp = amount * self.STAMP_DUTY if not is_buy else 0
        return commission + stamp

    def _calc_max_shares(self, price: float) -> int:
        """计算最大可买股数（按100股取整）"""
        est_cost_rate = self.COMMISSION + (0 if True else self.STAMP_DUTY)
        available = self.state.cash / (price * (1 + self.SLIPPAGE) * (1 + est_cost_rate))
        shares = int(available / 100) * 100
        return max(shares, 0)

    def _get_completed_trades(self) -> list[dict]:
        """获取已完成的买卖对"""
        result = []
        buy_stack = []
        for t in self.state.trades:
            if t.action == "buy":
                buy_stack.append(t)
            elif t.action == "sell":
                if buy_stack:
                    buy_trade = buy_stack.pop(0)
                    pnl = (t.price - buy_trade.price) * t.shares - t.cost - buy_trade.cost
                    result.append({
                        "entry_date": buy_trade.date,
                        "exit_date": t.date,
                        "entry_price": buy_trade.price,
                        "exit_price": t.price,
                        "shares": t.shares,
                        "pnl": pnl,
                        "pnl_pct": (t.price / buy_trade.price - 1) * 100,
                    })
        return result

    def _calc_max_drawdown(self) -> float:
        """计算最大回撤"""
        curve = self.get_equity_curve()
        if curve.empty:
            return 0.0
        values = curve["value"].values
        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd * 100
