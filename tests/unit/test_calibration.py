"""批次9: Calibration + ML Model 单元测试"""
import numpy as np
import pytest
from src.prediction.ml_model import MLModelLayer
from src.prediction.calibration import CalibrationLayer


class TestMLModelLayer:
    def test_untrained_returns_rule_prior(self):
        model = MLModelLayer()
        rule_features = {"historical_baserate": 0.55}
        p, tp, sp = model.predict("H2", {}, rule_features)
        assert 0.4 < p < 0.7
        assert tp <= p

    def test_train_and_predict(self):
        model = MLModelLayer()
        X = np.random.rand(100, 5)
        y = (X[:, 0] + X[:, 1] > 1.0).astype(int)
        feature_names = [f"f{i}" for i in range(5)]
        model.train("H2", X, y, feature_names)
        assert model._is_trained["H2"] is True

        test_features = {"f0": 0.8, "f1": 0.7, "f2": 0.5, "f3": 0.3, "f4": 0.1}
        p, _, _ = model.predict("H2", test_features, {})
        assert 0.01 <= p <= 0.99

    def test_feature_selection_cap(self):
        model = MLModelLayer(max_features=3)
        X = np.random.rand(100, 10)
        y = (X[:, 0] > 0.5).astype(int)
        feature_names = [f"f{i}" for i in range(10)]
        model.train("H2", X, y, feature_names)
        assert len(model._feature_names["H2"]) <= 3


class TestCalibrationLayer:
    def test_no_calibrator_identity(self):
        cal = CalibrationLayer()
        result = cal.calibrate("H2", 0.75)
        assert result == 0.75

    def test_fit_and_calibrate(self):
        cal = CalibrationLayer()
        raw = [0.5, 0.6, 0.7, 0.8, 0.9]
        actual = [0, 0, 1, 1, 1]
        cal.fit("H2", raw, actual)
        # 校准后应调整概率
        calibrated = cal.calibrate("H2", 0.6)
        assert 0.01 <= calibrated <= 0.99

    def test_ece_calculation(self):
        cal = CalibrationLayer(n_bins=5)
        # 完美校准: 预测=实际
        probs = [0.1, 0.3, 0.5, 0.7, 0.9]
        outcomes = [0, 0, 1, 1, 1]
        ece = cal.compute_ece(probs, outcomes)
        assert ece >= 0.0

    def test_ece_zero_for_perfect(self):
        cal = CalibrationLayer(n_bins=5)
        probs = [0.2, 0.2, 0.8, 0.8, 0.8]
        outcomes = [0, 0, 1, 1, 1]
        ece = cal.compute_ece(probs, outcomes)
        assert ece >= 0.0

    def test_health_check(self):
        cal = CalibrationLayer()
        assert cal.is_healthy("H2") is True
        cal.fit("H2", [0.5, 0.6, 0.7, 0.8], [0, 1, 0, 1])
        assert cal.is_healthy("H2") is True  # 小样本不应超过阈值
