#!/usr/bin/env python
"""SPAS 校准训练: 收集所有ETF的H2/L2信号 → 前向验证 → 拟合Isotonic校准器

产出:
- calibration_data.json: 校准数据 (raw_prob, outcome) 对
- 控制台输出: ECE报告 + 拟合状态
- CalibrationLayer 就绪, 可接入 PipelineOrchestrator
"""
import sys, io, json, asyncio, yaml
sys.path.insert(0, ".")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.prediction.calibration import CalibrationLayer

SYMBOLS = [
    "510300.SH", "159825.SZ", "515170.SH", "512010.SH", "512720.SH",
    "515880.SH", "159915.SZ", "510050.SH", "512880.SH", "515050.SH",
    "512480.SH", "159559.SZ", "159611.SZ",
]


async def collect_calibration_data():
    """遍历所有ETF, 收集每条确认信号+5日前向验证结果"""
    with open("config/settings.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    ms_cfg = cfg.get("market_state", {})
    setup_cfg = cfg.get("setup", {})
    horizon = cfg["prediction_horizon"]["optimal_days"]

    all_records = {"H2": [], "L2": []}
    adapter = LocalAdapter("data")

    for symbol in SYMBOLS:
        df = await adapter.get_bars(symbol, "day")
        if df.empty:
            continue

        # 构建bars
        bars = []
        for _, row in df.iterrows():
            bars.append(BarOHLCV(
                symbol=symbol,
                timestamp=row["timestamp"],
                timeframe=TimeFrame.DAY,
                open=Decimal(str(round(float(row["open"]), 4))),
                high=Decimal(str(round(float(row["high"]), 4))),
                low=Decimal(str(round(float(row["low"]), 4))),
                close=Decimal(str(round(float(row["close"]), 4))),
                volume=int(float(row["volume"])) if not pd.isna(row["volume"]) else 0,
                data_availability_time=row["timestamp"],
                source=DataSource.LOCAL,
            ))

        # 构建价格索引
        price_map = {}
        for b in bars:
            if isinstance(b.timestamp, datetime):
                price_map[b.timestamp.date()] = float(b.close)

        # 运行市场状态机 (带config参数)
        ms = MarketStateSvc(
            ema_period=ms_cfg.get("ema_period", 20),
            adx_period=ms_cfg.get("adx_period", 14),
            adx_threshold=ms_cfg.get("adx_threshold", 20),
            trend_ratio_bull=ms_cfg.get("trend_bar_ratio_bull", 0.40),
            trend_ratio_bear=ms_cfg.get("trend_bar_ratio_bear", 0.35),
            confirmation_bars=ms_cfg.get("confirmation_bars", 2),
            initial_confidence=ms_cfg.get("initial_confidence", 0.3),
            confidence_per_bar=ms_cfg.get("confidence_per_bar", 0.05),
            max_confidence=ms_cfg.get("max_confidence", 0.9),
        )

        # 运行Setup识别 (带config参数)
        sr = SetupRecogSvc(
            volume_shrink_ratio=setup_cfg.get("volume_shrink_ratio", 0.95),
            breakout_volume_multiplier=setup_cfg.get("breakout_volume_multiplier", 1.05),
            breakout_body_ratio=setup_cfg.get("breakout_body_ratio", 0.25),
        )

        re_engine = RuleEngine()
        state_at_bar: dict = {}  # bar_idx → MarketState

        # 逐Bar回放
        for i, bar in enumerate(bars):
            state = ms.update(bar)
            if state is not None:
                state_at_bar[i] = state  # 只记录状态变更点
            setup = sr.update(bar)

            if setup is None or not setup.is_confirmed:
                continue

            # 找到对应的市场状态 (最近的状态记录)
            current_state = None
            for idx in sorted(state_at_bar.keys(), reverse=True):
                if idx <= i:
                    current_state = state_at_bar[idx]
                    break

            if current_state is None:
                continue

            # 生成预测
            try:
                _, p_rule, confidence = re_engine.evaluate(
                    setup, current_state, float(bar.close)
                )
            except Exception:
                continue

            # 前向验证: 5天后实际涨跌
            signal_date = bar.timestamp.date() if isinstance(bar.timestamp, datetime) \
                else bar.timestamp
            future_date = signal_date + timedelta(days=horizon)

            # 找最近交易日
            future_price = None
            for offset in range(horizon, horizon + 10):
                check = signal_date + timedelta(days=offset)
                if check in price_map:
                    future_price = price_map[check]
                    break

            if future_price is None or float(bar.close) == 0:
                continue

            actual_ret = (future_price - float(bar.close)) / float(bar.close)
            actual_win = 1 if actual_ret > 0 else 0

            setup_type = setup.setup_type.value
            if setup_type not in all_records:
                continue

            all_records[setup_type].append({
                "symbol": symbol,
                "date": signal_date.strftime("%Y-%m-%d"),
                "setup_type": setup_type,
                "quality": float(setup.quality_score),
                "raw_prob": round(p_rule, 4),
                "market_state": current_state.state.value,
                "confidence": confidence,
                "actual_ret": round(actual_ret, 4),
                "actual_win": actual_win,
            })

    return all_records


async def main():
    print("=" * 60)
    print("  SPAS 校准训练 — Isotonic Regression Fitting")
    print("=" * 60)

    print(f"\n[1] 收集校准数据 (13只ETF, 5日前向验证)...")
    records = await collect_calibration_data()

    for setup_type in ["H2", "L2"]:
        n = len(records[setup_type])
        wins = sum(1 for r in records[setup_type] if r["actual_win"])
        wr = wins / n * 100 if n > 0 else 0
        print(f"  {setup_type}: {n}条信号, 实际胜率={wr:.1f}%")

    # 保存原始数据
    output_path = Path("data/calibration_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[2] 原始数据已保存: {output_path}")

    # 拟合校准器
    print(f"\n[3] 拟合 Isotonic Regression 校准器...")
    cal = CalibrationLayer(n_bins=10)

    for setup_type in ["H2", "L2"]:
        recs = records[setup_type]
        if len(recs) < 10:
            print(f"  {setup_type}: 样本不足 ({len(recs)}<10), 跳过拟合")
            continue

        raw_probs = [r["raw_prob"] for r in recs]
        outcomes = [r["actual_win"] for r in recs]

        cal.fit(setup_type, raw_probs, outcomes)
        ece = cal.get_ece(setup_type)
        healthy = cal.is_healthy(setup_type)

        print(f"  {setup_type}: 样本={len(recs)}  ECE={ece:.4f}  "
              f"健康={'OK' if healthy else '超标!'}")

        if healthy:
            # 打印校准映射
            test_probs = [0.45, 0.50, 0.52, 0.55, 0.60]
            for tp in test_probs:
                calibrated = cal.calibrate(setup_type, tp)
                print(f"    raw={tp:.2f} → calibrated={calibrated:.4f}")

    # 结论
    print(f"\n[4] 校准器就绪状态:")
    for setup_type in ["H2", "L2"]:
        ece = cal.get_ece(setup_type)
        if ece is not None:
            status = "已拟合" if cal.is_healthy(setup_type) else "ECE超标, 需重拟合"
        else:
            status = "未拟合 (样本不足)"
        print(f"  {setup_type}: {status}")

    print(f"\n{'=' * 60}")
    print(f"  校准训练完成")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
