"""批次8: RuleEngine单元测试 — Layer 1 规则引擎"""
from datetime import datetime
from decimal import Decimal
import pytest
from src.models.setup_signal import SetupSignal, SetupType, SetupStatus
from src.models.market_state import MarketState, MarketStateType
from src.prediction.rule_engine import RuleEngine


class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleEngine()

    def _make_h2(self, quality=Decimal("0.75"), status=SetupStatus.CONFIRMED):
        return SetupSignal(
            symbol="510300.SH", timestamp=datetime(2026,6,24,10,0),
            setup_type=SetupType.H2, candidate_vs_confirmed=status,
            quality_score=quality, maturity=3, detection_bar_index=100,
        )

    def _make_bull_state(self, confidence=Decimal("0.700")):
        return MarketState(
            symbol="510300.SH", timestamp=datetime(2026,6,24,10,0),
            timeframe="5min", state=MarketStateType.BULL,
            confidence=confidence, duration=10,
        )

    def test_evaluate_high_quality_h2_bull(self):
        """高质量H2+牛市→高置信度"""
        self.engine.update_baserate("H2", 0.65, 200)
        setup = self._make_h2(quality=Decimal("0.85"))
        state = self._make_bull_state(confidence=Decimal("0.800"))
        features, p_rule, confidence = self.engine.evaluate(setup, state, 3.5)
        assert features["is_setup"] is True
        assert confidence == "high"
        assert p_rule > 0.5

    def test_evaluate_low_quality(self):
        """低质量Setup→低置信度"""
        setup = self._make_h2(quality=Decimal("0.40"))
        state = self._make_bull_state()
        features, p_rule, confidence = self.engine.evaluate(setup, state, 3.5)
        assert confidence == "low"
        assert features["setup_quality"] < 0.5

    def test_small_sample_baserate(self):
        """冷启动: 样本量=0时使用先验值(0.55), 受趋势调节后不再强制0.5"""
        setup = self._make_h2(quality=Decimal("0.60"))
        state = self._make_bull_state()
        features, p_rule, confidence = self.engine.evaluate(setup, state, 3.5)
        assert features["sample_size"] == 0  # 初始为0
        # 修复后: baserate=0.55(H2先验)+0.05*0.7(BULL加分)=0.585
        assert features["historical_baserate"] == pytest.approx(0.585, abs=0.001)
        # 冷启动回归: p_rule = 0.5 + (0.585-0.5)*0.3 ≈ 0.5255
        assert p_rule > 0.5  # 不再精确等于0.5
        assert p_rule < 0.55  # 受回归限制, 不会太高

    def test_update_baserate(self):
        """更新胜率后应反映在evaluate中"""
        self.engine.update_baserate("H2", 0.65, 200)
        setup = self._make_h2(quality=Decimal("0.70"))
        state = self._make_bull_state()
        features, p_rule, confidence = self.engine.evaluate(setup, state, 3.5)
        assert features["historical_baserate"] >= 0.60  # 0.65 + trend bonus

    def test_build_prediction_output(self):
        """build_prediction应返回完整PredictionOutput"""
        self.engine.update_baserate("H2", 0.65, 200)
        setup = self._make_h2(quality=Decimal("0.80"))
        state = self._make_bull_state(confidence=Decimal("0.750"))
        pred = self.engine.build_prediction(setup, state, 3.5)
        assert pred.setup_type == "H2"
        assert float(pred.direction_prob) > 0.5
        assert float(pred.r_r_ratio) > 0
        assert float(pred.expected_value) != 0

    def test_p_rule_bounded(self):
        """P_rule应在[0.01, 0.99]区间"""
        setup = self._make_h2(quality=Decimal("0.50"))
        state = self._make_bull_state(confidence=Decimal("0.300"))
        _, p_rule, _ = self.engine.evaluate(setup, state, 3.5)
        assert 0.01 <= p_rule <= 0.99

    def test_l2_bear_alignment(self):
        """L2+熊市→趋势对齐"""
        setup = SetupSignal(
            symbol="510300.SH", timestamp=datetime(2026,6,24,10,0),
            setup_type=SetupType.L2, candidate_vs_confirmed=SetupStatus.CONFIRMED,
            quality_score=Decimal("0.70"), maturity=3, detection_bar_index=100,
        )
        state = MarketState(
            symbol="510300.SH", timestamp=datetime(2026,6,24,10,0),
            timeframe="5min", state=MarketStateType.BEAR,
            confidence=Decimal("0.700"), duration=10,
        )
        features, p_rule, _ = self.engine.evaluate(setup, state, 3.5)
        assert features["trend_aligned"] is True
