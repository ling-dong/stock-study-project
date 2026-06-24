"""§6.1.2 波动率锚定仓位缩放

仓位 = f(E[R]) * (σ_normal / σ_current)^0.5
"""
import numpy as np


class VolatilityAnchor:
    """波动率锚定 — §6.1.2"""

    def __init__(self, normal_window: int = 20, current_window: int = 5,
                 decay_exponent: float = 0.5, max_cap_at_high_vol: float = 0.05):
        self.normal_window = normal_window
        self.current_window = current_window
        self.decay_exponent = decay_exponent
        self.max_cap_at_high_vol = max_cap_at_high_vol

    def scale_position(self, returns_20d: list, returns_5d: list, base_position: float) -> float:
        """波动率锚定仓位缩放"""
        if len(returns_20d) < 5:
            return base_position

        sigma_normal = float(np.std(returns_20d)) if returns_20d else 0.01
        sigma_current = float(np.std(returns_5d)) if returns_5d else sigma_normal

        if sigma_normal <= 0:
            return base_position

        ratio = sigma_normal / sigma_current
        scale = ratio ** self.decay_exponent

        # 高波动率硬约束
        percentile_90 = float(np.percentile(returns_20d, 90)) if len(returns_20d) > 0 else 0.02
        if sigma_current > 1.5 * sigma_normal:
            scale = min(scale, 0.5)
        if sigma_current > percentile_90 * 2:
            return min(base_position * scale, self.max_cap_at_high_vol)

        return base_position * scale
