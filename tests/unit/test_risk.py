"""批次11: 风控体系单元测试"""
import pytest
from src.risk.constraints import RiskConstraints, PortfolioState, kelly_criterion, kelly_position
from src.risk.volatility import VolatilityAnchor
from src.risk.tail_risk import TailRiskManager, CircuitBreaker
from src.risk.liquidity import LiquidityMonitor
from src.risk.failure_detect import FailureDetector


class TestRiskConstraints:
    def test_l4_max_drawdown_blocks_all(self):
        rc = RiskConstraints()
        state = PortfolioState(max_drawdown=-0.25)
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert not ok
        assert "L4" in reason
        assert pos == 0.0

    def test_l1_daily_stop_blocks_new(self):
        rc = RiskConstraints()
        state = PortfolioState(daily_pnl=-0.04)
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert ok  # allows existing but...
        assert pos == 0.0  # no new positions

    def test_normal_passes(self):
        rc = RiskConstraints()
        state = PortfolioState()
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert ok
        assert pos == 0.10

    def test_l5_sector_limit(self):
        rc = RiskConstraints()
        state = PortfolioState(sector_exposures={"510300.SH": 0.15})
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert not ok  # 0.15 + 0.10 = 0.25 > 0.20
        assert "L5" in reason

    def test_l6_total_limit(self):
        rc = RiskConstraints()
        state = PortfolioState(total_exposure=0.75)
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert not ok  # 0.75 + 0.10 = 0.85 > 0.80
        assert "L6" in reason

    def test_consecutive_losses(self):
        rc = RiskConstraints()
        state = PortfolioState(consecutive_losses=3)
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert ok
        assert pos == 0.05  # halved

        state.consecutive_losses = 5
        ok, reason, pos = rc.evaluate("510300.SH", 0.10, state)
        assert not ok
        assert "5次亏损" in reason


class TestKelly:
    def test_kelly_positive(self):
        f = kelly_criterion(0.55, 2.0)
        assert f > 0

    def test_kelly_negative_edge(self):
        f = kelly_criterion(0.45, 1.0)
        assert f == 0.0

    def test_kelly_rr_filter(self):
        f = kelly_position(0.65, 0.5, min_rr=1.0)
        assert f == 0.0  # R:R < 1.0 filtered


class TestVolatilityAnchor:
    def test_high_vol_reduces(self):
        anchor = VolatilityAnchor()
        r20 = [0.001, 0.002] * 10  # low vol (small variance)
        r5 = [0.02, -0.01, 0.03, -0.015, 0.01]  # high vol
        pos = anchor.scale_position(r20, r5, 0.10)
        assert pos < 0.10  # reduced

    def test_normal_vol_unchanged(self):
        anchor = VolatilityAnchor()
        r = [0.002, 0.003] * 15  # consistent vol throughout
        pos = anchor.scale_position(r, r[-5:], 0.10)
        assert 0.09 <= pos <= 0.11


class TestTailRisk:
    def test_black_swan_vix(self):
        tm = TailRiskManager()
        triggered, action = tm.check_black_swan(0.97, 0.02, 0.01, 0.005)
        assert triggered
        assert "10%" in action

    def test_gap_triggers(self):
        tm = TailRiskManager()
        triggered, action = tm.check_black_swan(0.5, 0.01, 0.01, -0.04)
        assert triggered
        assert "跳空" in action

    def test_normal_no_trigger(self):
        tm = TailRiskManager()
        triggered, _ = tm.check_black_swan(0.5, 0.01, 0.01, 0.005)
        assert not triggered


class TestLiquidityMonitor:
    def test_spread_normal(self):
        lm = LiquidityMonitor()
        ok, _ = lm.check_spread(0.002, 0.001)
        assert ok

    def test_spread_abnormal(self):
        lm = LiquidityMonitor()
        ok, _ = lm.check_spread(0.005, 0.001)
        assert not ok

    def test_premium_ok(self):
        lm = LiquidityMonitor()
        ok, _ = lm.check_premium(1.015, 1.00)
        assert ok


class TestFailureDetector:
    def test_detection_all_clear(self):
        fd = FailureDetector()
        results = fd.detect(-0.05, 0.01, 0.01, 0.3, 0.001, 0.001)
        assert not fd.should_pause(results)

    def test_high_correlation_triggers(self):
        fd = FailureDetector()
        results = fd.detect(-0.05, 0.01, 0.01, 0.90, 0.001, 0.001)
        assert results["D4_correlation"][0]
        assert fd.should_pause(results)

    def test_winrate_deviation(self):
        fd = FailureDetector()
        for _ in range(20):
            fd.record_trade(0.60, False, "2026-06-24")  # all losses
        results = fd.detect(-0.05, 0.01, 0.01, 0.3, 0.001, 0.001)
        # predicted 0.6, actual 0.0, diff > 0.15
        assert results["D2_winrate"][0]
