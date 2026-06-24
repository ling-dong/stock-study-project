"""批次10: FusionLayer单元测试 — 动态权重+MTF投票"""
from datetime import datetime
from decimal import Decimal
import pytest
from src.prediction.fusion import FusionLayer
from src.models.prediction import PredictionOutput


class TestFusionLayer:
    def setup_method(self):
        self.fusion = FusionLayer()

    def test_small_sample_weights_rule_heavily(self):
        """小样本时规则权重应更高"""
        w_small = self.fusion.compute_dynamic_weight(sample_size=10, regime_similarity=1.0)
        w_large = self.fusion.compute_dynamic_weight(sample_size=1000, regime_similarity=1.0)
        assert w_small > w_large

    def test_low_similarity_weights_rule_heavily(self):
        """低regime相似度时规则权重应更高"""
        w_high_sim = self.fusion.compute_dynamic_weight(sample_size=200, regime_similarity=1.0)
        w_low_sim = self.fusion.compute_dynamic_weight(sample_size=200, regime_similarity=0.3)
        assert w_low_sim > w_high_sim

    def test_weight_in_range(self):
        """w_rule应在(0,1)区间"""
        for n in [10, 50, 200, 500, 2000]:
            for sim in [0.1, 0.5, 0.8, 1.0]:
                w = self.fusion.compute_dynamic_weight(n, sim)
                assert 0.0 < w < 1.0

    def test_fuse_no_divergence(self):
        """规则与ML概率接近时不应触发差异分析"""
        p_final, deviation = self.fusion.fuse(0.62, 0.65, 200, 0.9)
        assert deviation is None
        assert 0.60 < p_final < 0.67

    def test_fuse_with_divergence(self):
        """规则与ML概率差异>10%时应触发差异分析"""
        p_final, deviation = self.fusion.fuse(0.80, 0.55, 100, 0.8)
        assert deviation is not None
        assert "divergence" in deviation.lower()

    def test_mtf_vote_equal_weights(self):
        """等权重MTF投票"""
        preds = {
            "day": PredictionOutput(symbol="X", timestamp=datetime(2026,6,24,10,0),
                                    direction_prob=Decimal("0.7000"), target_prob=Decimal("0.5"),
                                    stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.0"),
                                    expected_value=Decimal("0.01"), setup_type="H2",
                                    model_version="v1"),
            "60min": PredictionOutput(symbol="X", timestamp=datetime(2026,6,24,10,0),
                                      direction_prob=Decimal("0.6000"), target_prob=Decimal("0.5"),
                                      stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.0"),
                                      expected_value=Decimal("0.01"), setup_type="H2",
                                      model_version="v1"),
        }
        prob = self.fusion.mtf_vote(preds)
        # 30+30权重: (0.7*0.3+0.6*0.3)/0.6=0.65
        assert 0.60 < prob < 0.70

    def test_mtf_vote_all_frameworks(self):
        """完整四框架投票"""
        preds = {}
        for tf in ["day", "60min", "15min", "5min"]:
            preds[tf] = PredictionOutput(
                symbol="X", timestamp=datetime(2026,6,24,10,0),
                direction_prob=Decimal("0.6500"), target_prob=Decimal("0.5"),
                stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.0"),
                expected_value=Decimal("0.01"), setup_type="H2", model_version="v1",
            )
        prob = self.fusion.mtf_vote(preds)
        assert prob == pytest.approx(0.65)

    def test_build_final_prediction(self):
        preds = {
            "day": PredictionOutput(symbol="510300.SH", timestamp=datetime(2026,6,24,10,0),
                                    direction_prob=Decimal("0.7000"), target_prob=Decimal("0.5"),
                                    stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.5"),
                                    expected_value=Decimal("0.01"), setup_type="H2",
                                    model_version="v1"),
        }
        result = self.fusion.build_final_prediction(
            "510300.SH", "H2", 0.65, 0.62, 200, preds, "model_v1",
        )
        assert result.setup_type == "H2"
        assert float(result.direction_prob) > 0
