"""§6.2.3 六维模型失效检测"""


class FailureDetector:
    """六维模型失效检测 — §6.2.3 表"""

    def __init__(self):
        self._recent_trades: list = []

    def record_trade(self, predicted_prob: float, actual_win: bool, trade_date: str):
        self._recent_trades.append({
            "predicted": predicted_prob, "actual": actual_win, "date": trade_date,
        })
        if len(self._recent_trades) > 100:
            self._recent_trades = self._recent_trades[-100:]

    def detect(self, current_drawdown: float, current_volatility: float,
               training_volatility: float, avg_correlation: float,
               bid_ask_spread: float, normal_spread: float) -> dict:
        """六维检测

        Returns: {dimension: (triggered, detail)}
        """
        results = {}

        # D1: 最大回撤
        results["D1_drawdown"] = (
            abs(current_drawdown) > 0.15,
            f"回撤{current_drawdown:.1%}"
        )

        # D2: 胜率偏离
        if len(self._recent_trades) >= 20:
            recent = self._recent_trades[-20:]
            actual_wr = sum(1 for t in recent if t["actual"]) / len(recent)
            predicted_wr = sum(t["predicted"] for t in recent) / len(recent)
            results["D2_winrate"] = (
                abs(actual_wr - predicted_wr) > 0.15,
                f"实际胜率{actual_wr:.2f} vs 预测{predicted_wr:.2f}"
            )
        else:
            results["D2_winrate"] = (False, "样本不足")

        # D3: 波动率突破
        if training_volatility > 0:
            vol_ratio = current_volatility / training_volatility
            results["D3_volatility"] = (
                vol_ratio > 2.0,
                f"波动率{current_volatility:.4f} vs 训练{training_volatility:.4f}"
            )
        else:
            results["D3_volatility"] = (False, "无训练波动率")

        # D4: 相关性异常
        results["D4_correlation"] = (
            avg_correlation > 0.85,
            f"板块间相关性{avg_correlation:.2f}"
        )

        # D5: 流动性
        if normal_spread > 0:
            spread_ratio = bid_ask_spread / normal_spread
            results["D5_liquidity"] = (
                spread_ratio > 3.0,
                f"价差比{spread_ratio:.1f}"
            )
        else:
            results["D5_liquidity"] = (False, "无价差基准")

        # D6: 预测置信度
        if len(self._recent_trades) >= 10:
            recent_probs = [t["predicted"] for t in self._recent_trades[-10:]]
            prob_std = sum((p - sum(recent_probs)/len(recent_probs))**2 for p in recent_probs) / len(recent_probs)
            results["D6_confidence"] = (
                prob_std > 0.1,
                f"概率方差{prob_std:.4f}"
            )
        else:
            results["D6_confidence"] = (False, "样本不足")

        return results

    def should_pause(self, detection_results: dict) -> bool:
        """任一维度触发则建议暂停"""
        return any(v[0] for v in detection_results.values())
