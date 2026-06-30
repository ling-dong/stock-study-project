"""§4.3.1 Rule Engine — Layer 1 规则引擎

输出结构化多维特征向量(非单一先验概率)，供ML模型层使用。
延迟预算: <50ms, 触发条件: 每次K线闭合(100%)。
"""
from datetime import datetime
from typing import Optional, Dict, Tuple
from src.models.setup_signal import SetupSignal, SetupType
from src.models.prediction import PredictionOutput
from src.models.market_state import MarketState, MarketStateType


class RuleEngine:
    """规则引擎 — §4.3.1 Layer 1

    输出多维规则特征而非单一概率:
    - is_setup: 是否存在已确认Setup
    - setup_quality: 结构质量评分[0,1]
    - historical_baserate: 历史基础胜率(sample<100时=0.5)
    - sample_size: 历史样本量
    """

    def __init__(self, sample_threshold: int = 100,
                 base_winrate_h2: float = 0.55,
                 base_winrate_l2: float = 0.55,
                 base_winrate_fb: float = 0.45):
        self.sample_threshold = sample_threshold
        # 先验基准胜率(设计文档要求删除未验证数字，此处为占位值，由回测系统更新)
        self._baserates: Dict[str, float] = {
            "H2": base_winrate_h2,
            "L2": base_winrate_l2,
            "FB": base_winrate_fb,
        }
        self._sample_counts: Dict[str, int] = {"H2": 0, "L2": 0, "FB": 0}

    def evaluate(
        self,
        setup: SetupSignal,
        market_state: MarketState,
        current_price: float,
        atr: float = 0.01,
    ) -> Tuple[dict, float, str]:
        """评估Setup并输出规则特征 + 概率 + 置信度

        冷启动修复 (§4.3.1 修订):
        - 先验概率从 0.55(H2)/0.55(L2)/0.45(FB) 起步 (非0.5)
        - 市场状态调节 / 趋势对齐 始终生效 (不再被 sample_size 阻塞)
        - 小样本时回归因子降低 (0.3 vs 0.7)，避免过度自信

        Args:
            setup: 已确认的SetupSignal
            market_state: 当前市场状态
            current_price: 当前价格
            atr: ATR值(用于目标/止损计算)

        Returns:
            (rule_features, P_rule, confidence_level)
        """
        # 1. 基础特征
        is_setup = setup.is_confirmed
        setup_quality = float(setup.quality_score)
        setup_type_str = setup.setup_type.value
        sample_size = self._sample_counts.get(setup_type_str, 0)
        baserate = self._baserates.get(setup_type_str, 0.5)

        # 2. 基准概率: 先验(0.55/0.55/0.45) vs 回测验证值
        #    冷启动时使用先验值而非0.5，避免信号完全无信息
        if sample_size >= self.sample_threshold:
            p_base = baserate           # 回测验证后的真实胜率
            sample_sufficient = True
        else:
            p_base = baserate           # 先验值 (H2=0.55, L2=0.55, FB=0.45)
            sample_sufficient = False

        # 3. 趋势对齐调整 — 始终生效
        #    H2+BULL / L2+BEAR 额外加分; FB+非趋势 额外加分
        #    加权: 市场状态置信度越高, 加分越多
        trend_aligned = self._check_trend_alignment(setup, market_state)
        mc = float(market_state.confidence)

        if trend_aligned:
            p_base = min(p_base + 0.05 * mc, 0.95)
        elif market_state.state == MarketStateType.NEUTRAL:
            # NEUTRAL时向0.5回拉, 不确定性越高惩罚越重
            p_base = max(p_base - 0.05 * (1.0 - mc), 0.30)

        # 4. 小样本回归 — 向0.5收缩
        #    样本充分: 信任信号 (regress=0.7)
        #    冷启动:   保守收缩 (regress=0.3)
        regress_factor = 0.7 if sample_sufficient else 0.3
        p_rule = 0.5 + (p_base - 0.5) * regress_factor

        # 5. 置信度判定
        if setup_quality >= 0.8 and trend_aligned and market_state.is_trending:
            confidence = "high"
        elif setup_quality >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        rule_features = {
            "is_setup": is_setup,
            "setup_quality": setup_quality,
            "historical_baserate": p_base,   # 调节后的基准概率(不含回归)
            "sample_size": sample_size,
            "trend_aligned": trend_aligned,
            "market_state": market_state.state.value,
            "market_confidence": float(market_state.confidence),
        }

        return rule_features, min(max(p_rule, 0.01), 0.99), confidence

    def build_prediction(
        self,
        setup: SetupSignal,
        market_state: MarketState,
        current_price: float,
        atr: float = 0.01,
        target_multiplier: float = 2.0,
        stop_multiplier: float = 1.0,
    ) -> PredictionOutput:
        """构建完整预测输出(含RRR和期望收益)"""
        features, p_rule, confidence = self.evaluate(setup, market_state, current_price, atr)

        # 目标收益 = ATR * 倍数
        target_dist = atr * target_multiplier
        stop_dist = atr * stop_multiplier
        r_r_ratio = target_dist / stop_dist if stop_dist > 0 else 1.0

        # 简化的期望收益(完整版在ML融合后计算)
        p_win = p_rule
        p_lose = 1.0 - p_win
        expected_value = p_win * target_dist - p_lose * stop_dist

        return PredictionOutput(
            symbol=setup.symbol,
            timestamp=setup.timestamp,
            direction_prob=round(p_rule, 4),
            target_prob=round(p_rule * 0.7, 4),
            stop_prob=round((1 - p_rule) * 0.8, 4),
            r_r_ratio=round(r_r_ratio, 3),
            expected_value=round(expected_value, 6),
            setup_type=setup.setup_type.value,
            model_version="rule_engine_v1",
            raw_probability=round(p_rule, 4),
            confidence_level=confidence,
        )

    def update_baserate(self, setup_type: str, new_rate: float, sample_count: int):
        """更新历史胜率(由回测系统调用)"""
        self._baserates[setup_type] = new_rate
        self._sample_counts[setup_type] = sample_count

    def _check_trend_alignment(self, setup: SetupSignal, market_state: MarketState) -> bool:
        """检查Setup与市场趋势是否对齐"""
        if setup.setup_type == SetupType.H2:
            return market_state.state == MarketStateType.BULL
        elif setup.setup_type == SetupType.L2:
            return market_state.state == MarketStateType.BEAR
        elif setup.setup_type == SetupType.FB:
            return not market_state.is_trending
        return False
