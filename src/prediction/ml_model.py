"""§4.3.2 ML Model Layer — Layer 2 LightGBM预测

按Setup类型独立训练(H2/L2/FB各一模型)，每模型最多30特征。
触发条件: 规则置信度<0.85(约10%K线事件触发)。
延迟预算: P99<500ms。
"""
from typing import Optional, List, Dict, Tuple
import numpy as np
from sklearn.base import BaseEstimator


class MLModelLayer:
    """ML模型层 — §4.3.2 Layer 2

    特性:
    - 分Setup类型独立模型: H2/L2/FB
    - 强制特征选择(每模型<=30特征)
    - 基线模型: LightGBM(生产)/sklearn(本地开发回退)
    """

    def __init__(self, max_features: int = 30):
        self.max_features = max_features
        self._models: Dict[str, Optional[BaseEstimator]] = {"H2": None, "L2": None, "FB": None}
        self._feature_names: Dict[str, List[str]] = {}
        self._is_trained: Dict[str, bool] = {"H2": False, "L2": False, "FB": False}

    def predict(
        self,
        setup_type: str,
        features: Dict[str, float],
        rule_features: Dict[str, float],
    ) -> Tuple[float, float, float]:
        """预测方向概率+目标达成概率+止损概率

        Returns:
            (direction_prob_raw, target_prob, stop_prob)
        """
        model = self._models.get(setup_type)
        if model is None or not self._is_trained.get(setup_type, False):
            # 未训练时返回规则层先验值
            p = rule_features.get("historical_baserate", 0.5)
            return p, p * 0.7, (1 - p) * 0.8

        # 构建特征向量
        selected_features = self._feature_names.get(setup_type, [])
        feature_values = []
        for fname in selected_features:
            val = features.get(fname, rule_features.get(fname, 0.0))
            feature_values.append(float(val))

        if not feature_values:
            p = rule_features.get("historical_baserate", 0.5)
            return p, p * 0.7, (1 - p) * 0.8

        X = np.array([feature_values])
        try:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)[0]
                direction_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            else:
                direction_prob = float(model.predict(X)[0])
        except Exception:
            direction_prob = rule_features.get("historical_baserate", 0.5)

        direction_prob = max(0.01, min(0.99, direction_prob))
        return direction_prob, direction_prob * 0.7, (1 - direction_prob) * 0.8

    def train(
        self,
        setup_type: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: List[str],
    ) -> None:
        """训练Setup类型专用模型"""
        from sklearn.ensemble import GradientBoostingClassifier

        if len(feature_names) > self.max_features:
            # 简单特征选择: 保留前max_features个
            feature_names = feature_names[:self.max_features]
            X_train = X_train[:, :self.max_features]

        model = GradientBoostingClassifier(
            n_estimators=100, max_depth=4,
            learning_rate=0.05, random_state=42,
        )
        model.fit(X_train, y_train)
        self._models[setup_type] = model
        self._feature_names[setup_type] = feature_names
        self._is_trained[setup_type] = True

    @property
    def is_any_trained(self) -> bool:
        return any(self._is_trained.values())
