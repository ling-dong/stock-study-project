"""配置管理 — YAML加载 + Pydantic校验"""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class RiskConstraintsConfig(BaseModel):
    L1_daily_stop: float = -0.03
    L2_weekly_stop: float = -0.08
    L3_monthly_stop: float = -0.15
    L4_max_drawdown: float = -0.20
    L5_single_sector_pct: float = 0.20
    L6_total_exposure_pct: float = 0.80


class KellyConfig(BaseModel):
    fraction: float = 0.25
    min_rr_ratio: float = 1.0


class VolatilityAnchorConfig(BaseModel):
    normal_window: int = 20
    current_window: int = 5
    decay_exponent: float = 0.5
    max_position_cap_at_high_vol: float = 0.05


class MarketStateConfig(BaseModel):
    ema_period: int = 20
    trend_bar_ratio_bull: float = 0.6
    trend_bar_ratio_bear: float = 0.4
    adx_period: int = 14
    adx_threshold: int = 25
    confirmation_bars: int = 2
    max_confidence: float = 0.9
    confidence_per_bar: float = 0.05
    initial_confidence: float = 0.3


class SetupConfig(BaseModel):
    volume_shrink_ratio: float = 0.8
    breakout_volume_multiplier: float = 1.2
    breakout_body_ratio: float = 0.5
    quality_weights: dict = Field(default_factory=lambda: {
        "pullback_similarity": 0.35,
        "volume_shrink": 0.30,
        "breakout_momentum": 0.35,
    })


class CalibrationConfig(BaseModel):
    ece_threshold: float = 0.01
    ece_retrain: float = 0.02
    ece_freeze: float = 0.05
    n_bins: int = 10
    refit_window_days: int = 60


class BacktestConfig(BaseModel):
    min_samples: int = 1000
    min_years: int = 5
    walk_forward_window_months: int = 1
    initial_train_months: int = 6
    forward_bias_threshold_severe: float = 0.30
    forward_bias_threshold_moderate: float = 0.10


class TradingCostsConfig(BaseModel):
    commission_bps: float = 0.25
    stamp_duty_bps: float = 1.0
    slippage_min_bps: float = 0.5
    slippage_max_bps: float = 1.5
    impact_cost_min_bps: float = 1.0
    impact_cost_max_bps: float = 5.0
    margin_rate_annual: float = 0.07


class AppConfig(BaseModel):
    """全局应用配置"""
    risk_constraints: RiskConstraintsConfig = Field(default_factory=RiskConstraintsConfig)
    kelly: KellyConfig = Field(default_factory=KellyConfig)
    volatility_anchor: VolatilityAnchorConfig = Field(default_factory=VolatilityAnchorConfig)
    market_state: MarketStateConfig = Field(default_factory=MarketStateConfig)
    setup: SetupConfig = Field(default_factory=SetupConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    trading_costs: TradingCostsConfig = Field(default_factory=TradingCostsConfig)


def load_config(config_dir: str = "config") -> AppConfig:
    """从YAML文件加载配置"""
    import yaml
    config_path = Path(config_dir) / "settings.yaml"
    if not config_path.exists():
        return AppConfig()

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    sections = {}
    section_map = {
        "risk_constraints": RiskConstraintsConfig,
        "kelly": KellyConfig,
        "volatility_anchor": VolatilityAnchorConfig,
        "market_state": MarketStateConfig,
        "setup": SetupConfig,
        "calibration": CalibrationConfig,
        "backtest": BacktestConfig,
        "trading_costs": TradingCostsConfig,
    }

    for key, cls in section_map.items():
        if key in raw:
            sections[key] = cls(**raw[key])

    return AppConfig(**sections)
