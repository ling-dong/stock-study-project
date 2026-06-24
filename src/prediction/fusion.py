"""§4.3.3 融合决策层 — 规则+ML动态权重 + MTF四框架投票

动态权重公式:
  w_rule = sigmoid(0.5*(1-n/500) + 0.5*(1-sim_regime))
  P_final = w_rule * P_rule + (1-w_rule) * P_ml

MTF投票权重: 日线30%, 60分钟30%, 15分钟20%, 5分钟20%
"""
from typing import Optional, Dict, List, Tuple
import math
from src.models.prediction import PredictionOutput


class FusionLayer:
    """融合决策层 — §4.3.3

    特性:
    - 动态权重: 基于样本量和regime相似度
    - MTF四框架投票
    - 规则-ML矛盾检测(差异>10%触发差异分析)
    """

    def __init__(self, mtf_weights: Optional[Dict[str, float]] = None):
        self.mtf_weights = mtf_weights or {
            "day": 0.30, "60min": 0.30, "15min": 0.20, "5min": 0.20,
        }

    def compute_dynamic_weight(
        self,
        sample_size: int,
        regime_similarity: float = 1.0,
    ) -> float:
        """计算规则引擎动态权重

        Args:
            sample_size: 历史样本量
            regime_similarity: 当前市场体制与训练期的相似度[0,1]

        Returns:
            w_rule ∈ (0, 1)
        """
        x = 0.5 * (1.0 - sample_size / 500.0) + 0.5 * (1.0 - regime_similarity)
        return 1.0 / (1.0 + math.exp(-x))  # sigmoid

    def fuse(
        self,
        p_rule: float,
        p_ml: float,
        sample_size: int,
        regime_similarity: float = 1.0,
    ) -> Tuple[float, Optional[str]]:
        """融合规则与ML概率

        Returns:
            (P_final, deviation_analysis)
        """
        w_rule = self.compute_dynamic_weight(sample_size, regime_similarity)
        p_final = w_rule * p_rule + (1.0 - w_rule) * p_ml

        # 差异分析
        deviation = None
        if abs(p_rule - p_ml) > 0.10:
            deviation = (
                f"Rule-ML divergence: P_rule={p_rule:.4f}, P_ml={p_ml:.4f}, "
                f"w_rule={w_rule:.3f}, P_final={p_final:.4f}"
            )

        return p_final, deviation

    def mtf_vote(
        self,
        predictions: Dict[str, PredictionOutput],
    ) -> float:
        """多时间框架加权投票

        Args:
            predictions: {timeframe: PredictionOutput}

        Returns:
            加权融合方向概率
        """
        weighted_prob = 0.0
        total_weight = 0.0

        for tf, pred in predictions.items():
            weight = self.mtf_weights.get(tf, 0.0)
            if weight > 0:
                weighted_prob += weight * float(pred.direction_prob)
                total_weight += weight

        if total_weight > 0:
            return weighted_prob / total_weight
        return 0.5

    def build_final_prediction(
        self,
        symbol: str,
        setup_type: str,
        p_rule: float,
        p_ml: float,
        sample_size: int,
        mtf_predictions: Dict[str, PredictionOutput],
        model_version: str,
        regime_similarity: float = 1.0,
    ) -> PredictionOutput:
        """构建最终预测输出(含融合+MFT投票)

        Returns:
            融合后的PredictionOutput
        """
        # 规则-ML融合
        p_fused, deviation = self.fuse(p_rule, p_ml, sample_size, regime_similarity)

        # MTF投票
        mtf_prob = self.mtf_vote(mtf_predictions)

        # 最终概率 = 融合概率与MTF概率的平均
        p_final = (p_fused + mtf_prob) / 2.0

        # 取第一个预测的结构信息
        base_pred = list(mtf_predictions.values())[0] if mtf_predictions else None
        r_r = float(base_pred.r_r_ratio) if base_pred else 1.0
        ev = float(base_pred.expected_value) if base_pred else 0.0

        # 置信度
        if abs(p_rule - p_ml) < 0.05:
            conf = "high"
        elif abs(p_rule - p_ml) < 0.15:
            conf = "medium"
        else:
            conf = "low"

        return PredictionOutput(
            symbol=symbol,
            timestamp=base_pred.timestamp if base_pred else None,
            direction_prob=round(p_final, 4),
            target_prob=round(p_final * 0.7, 4),
            stop_prob=round((1.0 - p_final) * 0.8, 4),
            r_r_ratio=round(r_r, 3),
            expected_value=round(ev, 6),
            setup_type=setup_type,
            model_version=model_version,
            raw_probability=round(p_ml, 4),
            confidence_level=conf,
        )
