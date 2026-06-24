"""§4.6.1 前视偏差检测"""
import numpy as np


class ForwardBiasDetector:
    """前视偏差检测 — §4.6.1"""

    def __init__(self, severe_threshold: float = 0.30, moderate_threshold: float = 0.10):
        self.severe_threshold = severe_threshold
        self.moderate_threshold = moderate_threshold

    def detect(self, walk_forward_metric: float, full_sample_metric: float) -> dict:
        """比较Walk-Forward与全量计算的性能差异"""
        if full_sample_metric == 0:
            return {"bias": 0.0, "level": "unknown"}

        bias = abs(walk_forward_metric - full_sample_metric) / abs(full_sample_metric)
        if bias > self.severe_threshold:
            level = "severe"
        elif bias > self.moderate_threshold:
            level = "moderate"
        else:
            level = "clean"

        return {"bias": round(bias, 4), "level": level}

    def is_severe(self, result: dict) -> bool:
        return result.get("level") == "severe"
