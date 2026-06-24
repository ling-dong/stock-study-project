"""§4.3.2 概率校准层 — Layer 3 Isotonic Regression

将ML原始概率映射为经验校准概率。
月度重拟合，ECE目标<0.01。
"""
from typing import Optional, Tuple, List
import numpy as np
from sklearn.isotonic import IsotonicRegression


class CalibrationLayer:
    """概率校准层 — §4.3.2 Layer 3

    特性:
    - Isotonic Regression保序校准
    - ECE(Expected Calibration Error)追踪
    - 月度重拟合(60个交易日)
    - ECE>0.02触发重训练，ECE>0.05暂停交易
    """

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
        self._calibrators: dict = {}  # setup_type -> IsotonicRegression
        self._ece_values: dict = {}  # setup_type -> latest ECE

    def calibrate(self, setup_type: str, raw_prob: float) -> float:
        """校准单个概率值"""
        cal = self._calibrators.get(setup_type)
        if cal is None:
            return raw_prob  # 未拟合时恒等映射
        try:
            calibrated = float(cal.predict([raw_prob])[0])
            return max(0.01, min(0.99, calibrated))
        except Exception:
            return raw_prob

    def fit(self, setup_type: str, raw_probs: List[float], actual_outcomes: List[int]):
        """拟合Isotonic Regression校准器"""
        if len(raw_probs) < 10:
            return
        cal = IsotonicRegression(y_min=0.01, y_max=0.99, out_of_bounds="clip")
        X = np.array(raw_probs, dtype=float)
        y = np.array(actual_outcomes, dtype=float)
        cal.fit(X, y)
        self._calibrators[setup_type] = cal
        self._ece_values[setup_type] = self.compute_ece(raw_probs, actual_outcomes)

    def compute_ece(self, raw_probs: List[float], actual_outcomes: List[int]) -> float:
        """计算Expected Calibration Error"""
        if len(raw_probs) == 0:
            return 0.0
        probs = np.array(raw_probs, dtype=float)
        outcomes = np.array(actual_outcomes, dtype=float)
        bins = np.linspace(0, 1, self.n_bins + 1)
        ece = 0.0
        n = len(probs)
        for i in range(self.n_bins):
            mask = (probs >= bins[i]) & (probs < bins[i+1])
            bin_size = mask.sum()
            if bin_size > 0:
                avg_pred = probs[mask].mean()
                avg_actual = outcomes[mask].mean()
                ece += (bin_size / n) * abs(avg_pred - avg_actual)
        return float(ece)

    def get_ece(self, setup_type: str) -> Optional[float]:
        return self._ece_values.get(setup_type)

    def is_healthy(self, setup_type: str, freeze_threshold: float = 0.05) -> bool:
        """ECE是否在健康范围(<=0.05)"""
        ece = self._ece_values.get(setup_type)
        if ece is None:
            return True
        return ece <= freeze_threshold
