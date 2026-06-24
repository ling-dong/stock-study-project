"""§4.6 回测绩效指标"""
import numpy as np
from typing import List
from src.models.backtest import BacktestRecord


class BacktestMetrics:
    """回测绩效指标计算"""

    @staticmethod
    def win_rate(records: List[BacktestRecord]) -> float:
        wins = sum(1 for r in records if r.is_win)
        return wins / len(records) if records else 0.0

    @staticmethod
    def sharpe_ratio(records: List[BacktestRecord]) -> float:
        returns = [float(r.net_pnl or 0) for r in records]
        if len(returns) < 2:
            return 0.0
        std = float(np.std(returns))
        return float(np.mean(returns)) / std if std > 0 else 0.0

    @staticmethod
    def max_drawdown(records: List[BacktestRecord]) -> float:
        cumulative = 1.0
        peak = 1.0
        max_dd = 0.0
        for r in records:
            cumulative *= (1.0 + float(r.net_pnl or 0))
            peak = max(peak, cumulative)
            dd = (cumulative - peak) / peak
            max_dd = min(max_dd, dd)
        return max_dd

    @staticmethod
    def brier_score(predictions: List[float], outcomes: List[int]) -> float:
        if not predictions:
            return 0.0
        return float(np.mean([(p - o) ** 2 for p, o in zip(predictions, outcomes)]))

    @staticmethod
    def profit_factor(records: List[BacktestRecord]) -> float:
        gross_win = sum(float(r.net_pnl or 0) for r in records if r.is_win)
        gross_loss = abs(sum(float(r.net_pnl or 0) for r in records if not r.is_win))
        return gross_win / gross_loss if gross_loss > 0 else float("inf")
