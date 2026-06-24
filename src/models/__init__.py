"""SPAS 数据模型 — 对应设计文档 §5"""
from src.models.bar import BarOHLCV, BarAdjustment, TimeFrame, DataSource
from src.models.feature import FeatureVector
from src.models.market_state import MarketState, MarketStateType, RegimeType
from src.models.setup_signal import SetupSignal, SetupType, SetupStatus
from src.models.prediction import PredictionOutput
from src.models.backtest import BacktestRecord
from src.models.sector_config import SectorConfig, ConstituentWeight
from src.models.version import SystemVersion

__all__ = [
    "BarOHLCV", "BarAdjustment", "TimeFrame", "DataSource",
    "FeatureVector",
    "MarketState", "MarketStateType", "RegimeType",
    "SetupSignal", "SetupType", "SetupStatus",
    "PredictionOutput",
    "BacktestRecord",
    "SectorConfig", "ConstituentWeight",
    "SystemVersion",
]
