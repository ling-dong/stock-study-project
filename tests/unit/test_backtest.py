"""批次12: 回测引擎单元测试"""
import pytest
from src.backtest.cost_model import CostModel
from src.backtest.forward_bias import ForwardBiasDetector
from src.backtest.metrics import BacktestMetrics
from src.backtest.engine import WalkForwardBacktest
from src.models.backtest import BacktestRecord
from tests.fixtures.sample_data import generate_bars


class TestCostModel:
    def test_round_trip_cost_positive(self):
        cm = CostModel()
        cost = cm.round_trip_cost(3.5)
        assert cost > 0

    def test_expected_value_calculation(self):
        cm = CostModel()
        ev = cm.expected_value(0.55, 0.35, 0.10, 0.03, -0.02)
        # 应产出合理期望值
        assert -0.10 < ev < 0.10

    def test_expected_value_all_loss(self):
        cm = CostModel()
        ev = cm.expected_value(0.0, 1.0, 0.0, 0.03, -0.02)
        assert ev < 0


class TestForwardBiasDetector:
    def test_no_bias(self):
        fd = ForwardBiasDetector()
        r = fd.detect(0.55, 0.56)
        assert r["level"] == "clean"

    def test_severe_bias(self):
        fd = ForwardBiasDetector()
        r = fd.detect(0.55, 0.90)
        assert r["level"] == "severe"
        assert fd.is_severe(r)

    def test_moderate_bias(self):
        fd = ForwardBiasDetector()
        r = fd.detect(0.55, 0.70)
        assert r["level"] == "moderate"


class TestBacktestMetrics:
    def _make_record(self, is_win: bool, net_pnl: float, idx: int = 1):
        from datetime import datetime
        from decimal import Decimal
        return BacktestRecord(
            version_id="v1", record_id=idx, symbol="510300.SH",
            entry_time=datetime(2026,6,24,10,0), entry_price=Decimal("3.5"),
            costs=Decimal("0.0025"), setup_type="H2",
            position_size=Decimal("0.1"),
            exit_time=datetime(2026,6,24,11,0), exit_price=Decimal("3.55"),
            pnl=Decimal(str(net_pnl)),
        )

    def test_win_rate(self):
        records = [self._make_record(True, 0.05, i) for i in range(3)]
        records += [self._make_record(False, -0.03, 4)]
        wr = BacktestMetrics.win_rate(records)
        assert wr == pytest.approx(0.75)

    def test_brier_score(self):
        preds = [0.8, 0.6, 0.4, 0.2]
        outcomes = [1, 1, 0, 0]
        bs = BacktestMetrics.brier_score(preds, outcomes)
        assert bs < 0.25

    def test_max_drawdown(self):
        records = [
            self._make_record(True, 0.01, 1),
            self._make_record(False, -0.02, 2),
            self._make_record(False, -0.03, 3),
        ]
        dd = BacktestMetrics.max_drawdown(records)
        assert dd < 0

    def test_profit_factor(self):
        records = [
            self._make_record(True, 0.05, 1),
            self._make_record(True, 0.03, 2),
            self._make_record(False, -0.02, 3),
        ]
        pf = BacktestMetrics.profit_factor(records)
        assert pf > 1.0


class TestWalkForwardBacktest:
    def test_empty_bars(self):
        wf = WalkForwardBacktest()
        result = wf.run([], None, None)
        assert result == []

    def test_insufficient_bars(self):
        wf = WalkForwardBacktest()
        bars = generate_bars(n_bars=10)
        result = wf.run(bars, None, None)
        assert result == []

    def test_get_summary_empty(self):
        wf = WalkForwardBacktest()
        summary = wf.get_summary()
        assert summary["total_trades"] == 0
