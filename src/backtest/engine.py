"""§4.6.1 Walk-Forward回测引擎"""
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import numpy as np
from decimal import Decimal
from src.models.bar import BarOHLCV
from src.models.backtest import BacktestRecord
from src.backtest.cost_model import CostModel


class WalkForwardBacktest:
    """Walk-Forward回测引擎 — §4.6.1"""

    def __init__(self, initial_train_months: int = 6, test_window_months: int = 1):
        self.initial_train_months = initial_train_months
        self.test_window_months = test_window_months
        self.cost_model = CostModel()
        self._records: List[BacktestRecord] = []
        self._record_counter: int = 0

    def run(self, bars: List[BarOHLCV], signal_generator, risk_evaluator) -> List[BacktestRecord]:
        """执行Walk-Forward回测

        Args:
            bars: 全量K线数据(按时间排序)
            signal_generator: (bars_window) -> List[Signal]
            risk_evaluator: (signal, state) -> (allowed, adjusted_pos)
        """
        if len(bars) < 30:
            return []

        # 按日期分割
        dates = sorted(set(b.timestamp.date() for b in bars))
        train_start = 0
        test_start = min(self.initial_train_months * 20, len(dates) - 5)  # ~20交易日/月

        while test_start < len(dates):
            test_end = min(test_start + self.test_window_months * 20, len(dates))
            train_bars = [b for b in bars if b.timestamp.date() <= dates[test_start - 1]]
            test_bars = [b for b in bars if dates[test_start] <= b.timestamp.date() <= dates[test_end - 1]]

            if len(train_bars) >= 30 and len(test_bars) >= 5:
                self._run_window(train_bars, test_bars, signal_generator, risk_evaluator)

            test_start = test_end

        return self._records

    def _run_window(self, train_bars: list, test_bars: list, signal_generator, risk_evaluator):
        """单窗口回测"""
        portfolio = {"cash": 1.0, "position": 0.0, "entry_price": 0.0,
                     "max_value": 1.0, "daily_pnl": 0.0, "consecutive_losses": 0}

        for bar in test_bars:
            signals = signal_generator(train_bars, bar)

            for sig in signals:
                allowed, adjusted_pos = risk_evaluator(sig, portfolio)
                if not allowed or adjusted_pos <= 0:
                    continue

                self._record_counter += 1
                self._records.append(self._simulate_trade(sig, bar, adjusted_pos, portfolio))

    def _simulate_trade(self, sig, bar, position: float, portfolio: dict) -> BacktestRecord:
        entry_price = float(bar.close)
        # 简化: 假设下一根Bar平仓
        exit_price = round(entry_price * (1.05 if sig.get("direction", "long") == "long" else 0.95), 4)
        pnl = round((exit_price - entry_price) * position / entry_price, 4)
        costs = round(self.cost_model.round_trip_cost(entry_price, position), 4)

        return BacktestRecord(
            version_id="System_v0.1", record_id=self._record_counter,
            symbol=bar.symbol, entry_time=bar.timestamp,
            exit_time=bar.timestamp + timedelta(hours=1),
            entry_price=Decimal(str(entry_price)), exit_price=Decimal(str(exit_price)),
            pnl=Decimal(str(pnl)), costs=Decimal(str(costs)),
            setup_type=sig.get("setup_type", "H2"),
            position_size=Decimal(str(round(position, 4))),
        )

    def get_summary(self) -> dict:
        if not self._records:
            return {"total_trades": 0, "win_rate": 0, "total_pnl": 0, "sharpe": 0}
        wins = sum(1 for r in self._records if r.is_win)
        total = len(self._records)
        total_pnl = sum(float(r.net_pnl or 0) for r in self._records)
        returns = [float(r.net_pnl or 0) for r in self._records]
        sharpe = float(np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0
        return {
            "total_trades": total, "win_rate": wins / total if total > 0 else 0,
            "total_pnl": round(total_pnl, 4),
            "sharpe": round(sharpe, 2),
            "avg_pnl": round(total_pnl / total, 6) if total > 0 else 0,
        }
