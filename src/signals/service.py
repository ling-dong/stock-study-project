"""SPAS API 服务层 — 封装核心预测、市场数据和回测能力

本模块不依赖任何 Web 框架，可被 FastAPI/Streamlit/CLI 直接调用，
保证 SPAS 核心逻辑只在一处实现。
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from src.config.loader import load_config
from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.risk.constraints import RiskConstraints, PortfolioState, kelly_position
from src.backtest.cost_model import CostModel
from src.backtest.metrics import BacktestMetrics
from src.pipeline.orchestrator import PipelineOrchestrator


@dataclass
class SPASAnalysisResult:
    symbol: str
    timestamp: datetime
    current_price: float
    market_state: dict
    setup_summary: dict
    prediction: Optional[dict]
    risk: Optional[dict]


class SPASService:
    """SPAS 核心服务 — 数据 → 特征 → 预测 → 风险"""

    def __init__(self, data_dir: str = "data", config_dir: str = "config"):
        self.data_dir = Path(data_dir)
        self.config = load_config(config_dir)
        self.adapter = LocalAdapter(data_dir)
        self.rule_engine = RuleEngine()
        self.risk_constraints = RiskConstraints()
        self.cost_model = CostModel()
        self.bar_feature_svc = BarFeatureSvc()

    async def _load_bars(self, code: str, freq: str = "day") -> list[BarOHLCV]:
        df = await self.adapter.get_bars(code, freq)
        if df.empty:
            return []

        bars = []
        for _, row in df.iterrows():
            ts = row["timestamp"]
            if isinstance(ts, pd.Timestamp):
                ts = ts.to_pydatetime()
            bars.append(
                BarOHLCV(
                    symbol=code,
                    timestamp=ts,
                    timeframe=TimeFrame.DAY if freq == "day" else TimeFrame.M5,
                    open=Decimal(str(round(float(row["open"]), 4))),
                    high=Decimal(str(round(float(row["high"]), 4))),
                    low=Decimal(str(round(float(row["low"]), 4))),
                    close=Decimal(str(round(float(row["close"]), 4))),
                    volume=int(float(row["volume"])) if not pd.isna(row.get("volume")) else 0,
                    data_availability_time=ts,
                    source=DataSource.LOCAL,
                )
            )
        return bars

    async def analyze_etf(self, code: str) -> Optional[SPASAnalysisResult]:
        """对指定 ETF 运行完整 SPAS 流水线，返回最新预测"""
        bars = await self._load_bars(code, "day")
        if len(bars) < 60:
            return None

        ms_config = self.config.market_state
        setup_config = self.config.setup

        # 1. 市场状态机
        ms = MarketStateSvc(
            ema_period=ms_config.ema_period,
            trend_ratio_bull=ms_config.trend_bar_ratio_bull,
            trend_ratio_bear=ms_config.trend_bar_ratio_bear,
            adx_period=ms_config.adx_period,
            adx_threshold=ms_config.adx_threshold,
            confirmation_bars=ms_config.confirmation_bars,
            max_confidence=ms_config.max_confidence,
            confidence_per_bar=ms_config.confidence_per_bar,
            initial_confidence=ms_config.initial_confidence,
        )
        final_state = None
        for b in bars:
            s = ms.update(b)
            if s is not None:
                final_state = s

        # 2. Setup 识别
        sr = SetupRecogSvc(
            volume_shrink_ratio=setup_config.volume_shrink_ratio,
            breakout_volume_multiplier=setup_config.breakout_volume_multiplier,
            breakout_body_ratio=setup_config.breakout_body_ratio,
            pullback_sim_weight=setup_config.quality_weights.get("pullback_similarity", 0.35),
            volume_shrink_weight=setup_config.quality_weights.get("volume_shrink", 0.30),
            breakout_momentum_weight=setup_config.quality_weights.get("breakout_momentum", 0.35),
        )
        all_setups = []
        for b in bars:
            sig = sr.update(b)
            if sig is not None:
                all_setups.append(sig)

        confirmed = [s for s in all_setups if s.is_confirmed]
        candidates = [s for s in all_setups if not s.is_confirmed]

        latest = bars[-1]
        current_price = float(latest.close)

        # 3. 预测与风险
        prediction = None
        risk = None
        if confirmed and final_state:
            last_sig = confirmed[-1]
            pred = self.rule_engine.build_prediction(last_sig, final_state, current_price)
            prediction = {
                "direction_prob": float(pred.direction_prob),
                "target_prob": float(pred.target_prob),
                "stop_prob": float(pred.stop_prob),
                "r_r_ratio": float(pred.r_r_ratio),
                "expected_value": float(pred.expected_value),
                "confidence_level": pred.confidence_level,
                "setup_type": pred.setup_type,
            }
            k_pos = kelly_position(float(pred.direction_prob), float(pred.r_r_ratio))
            ok, reason, allowed_pos = self.risk_constraints.evaluate(
                code, k_pos, PortfolioState()
            )
            risk = {
                "kelly_position": allowed_pos,
                "risk_ok": ok,
                "risk_reason": reason,
            }

        return SPASAnalysisResult(
            symbol=code,
            timestamp=latest.timestamp,
            current_price=current_price,
            market_state={
                "state": final_state.state.value if final_state else None,
                "confidence": float(final_state.confidence) if final_state else None,
                "duration": final_state.duration if final_state else None,
            },
            setup_summary={
                "confirmed_count": len(confirmed),
                "candidate_count": len(candidates),
                "latest_confirmed_date": confirmed[-1].timestamp.isoformat() if confirmed else None,
                "latest_candidate_date": candidates[-1].timestamp.isoformat() if candidates else None,
            },
            prediction=prediction,
            risk=risk,
        )

    async def list_etfs(self) -> list[dict]:
        """列出 data/ 目录下可用的 ETF"""
        etfs = []
        for f in sorted(self.data_dir.glob("*_day.parquet")):
            code = f.stem.replace("_day", "")
            etfs.append({
                "code": code,
                "market": "SH" if ".SH" in f.stem else "SZ",
                "file": str(f),
                "has_5min": (self.data_dir / f"{code}_5min.parquet").exists(),
            })
        return etfs

    async def get_ohlcv(self, code: str, freq: str = "day", limit: int = 180) -> list[dict]:
        """获取 ETF 的 OHLCV 数据，用于 K 线图"""
        df = await self.adapter.get_bars(code, freq)
        if df.empty:
            return []

        df = df.tail(limit).copy()
        bars = []
        for _, row in df.iterrows():
            ts = row["timestamp"]
            bars.append({
                "date": str(ts)[:10] if isinstance(ts, str) else ts.strftime("%Y-%m-%d"),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row.get("volume", 0)),
            })
        return bars

    async def get_etf_metadata(self) -> list[dict]:
        """获取所有 ETF 的元数据概览"""
        etfs = await self.list_etfs()
        records = []
        for etf in etfs:
            df = await self.adapter.get_bars(etf["code"], "day")
            if not df.empty:
                records.append({
                    "code": etf["code"],
                    "market": etf["market"],
                    "rows": len(df),
                    "start_date": str(df["timestamp"].iloc[0])[:10],
                    "end_date": str(df["timestamp"].iloc[-1])[:10],
                })
        return records

    def get_system_status(self) -> dict:
        """系统状态"""
        return {
            "version": "System_v0.1={rules_v1,model_v1,features_v1,data_v1}",
            "data_dir": str(self.data_dir.resolve()),
        }
