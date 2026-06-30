#!/usr/bin/env python
"""SPAS 前向验证 V2: 收集所有ETF的H2+L2信号 → N日前向结果 → 校准评估

对比修复前后的预测质量:
- 修复前: p_rule 锁死在50%, 毫无区分度
- 修复后: 市场状态调节生效, 概率有离散度 → 验证是否与实盘匹配
"""
import sys, io, asyncio, yaml
sys.path.insert(0, ".")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.prediction.calibration import CalibrationLayer

HORIZONS = [1, 3, 5, 10, 20]
SYMBOLS = [
    "510300.SH", "159825.SZ", "515170.SH", "512010.SH", "512720.SH",
    "515880.SH", "159915.SZ", "510050.SH", "512880.SH", "515050.SH",
    "512480.SH", "159559.SZ", "159611.SZ",
]


async def main():
    with open("config/settings.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    ms_cfg = cfg.get("market_state", {})
    setup_cfg = cfg.get("setup", {})

    print("=" * 70)
    print("  SPAS 前向验证 V2 — H2 + L2 信号全量检测")
    print("  修复后参数: ADX阈值=18, BULL=0.40, vol_shrink=0.95, body=0.25")
    print("=" * 70)

    # 收集所有信号 + 前向结果
    all_signals = []
    adapter = LocalAdapter("data")

    for symbol in SYMBOLS:
        df = await adapter.get_bars(symbol, "day")
        if df.empty:
            continue

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

        # 价格索引
        price_map = {}
        for b in bars:
            if isinstance(b.timestamp, datetime):
                price_map[b.timestamp.date()] = float(b.close)

        # 运行检测
        ms = MarketStateSvc(
            ema_period=ms_cfg.get("ema_period", 20),
            adx_period=ms_cfg.get("adx_period", 14),
            adx_threshold=ms_cfg.get("adx_threshold", 18),
            trend_ratio_bull=ms_cfg.get("trend_bar_ratio_bull", 0.40),
            trend_ratio_bear=ms_cfg.get("trend_bar_ratio_bear", 0.35),
            confirmation_bars=ms_cfg.get("confirmation_bars", 2),
            initial_confidence=ms_cfg.get("initial_confidence", 0.3),
            confidence_per_bar=ms_cfg.get("confidence_per_bar", 0.05),
            max_confidence=ms_cfg.get("max_confidence", 0.9),
        )
        sr = SetupRecogSvc(
            volume_shrink_ratio=setup_cfg.get("volume_shrink_ratio", 0.95),
            breakout_volume_multiplier=setup_cfg.get("breakout_volume_multiplier", 1.05),
            breakout_body_ratio=setup_cfg.get("breakout_body_ratio", 0.25),
        )
        re_engine = RuleEngine()
        state_at_bar = {}

        for i, bar in enumerate(bars):
            state = ms.update(bar)
            if state is not None:
                state_at_bar[i] = state
            setup = sr.update(bar)

            if setup is None or not setup.is_confirmed:
                continue

            # 找到对应市场状态
            current_state = None
            for idx in sorted(state_at_bar.keys(), reverse=True):
                if idx <= i:
                    current_state = state_at_bar[idx]
                    break
            if current_state is None:
                continue

            # 生成预测
            _, p_rule, confidence = re_engine.evaluate(
                setup, current_state, float(bar.close)
            )

            # 前向验证: 各期限实际结果
            signal_date = bar.timestamp.date() if isinstance(bar.timestamp, datetime) else bar.timestamp
            signal_price = float(bar.close)

            outcomes = {}
            for horizon in HORIZONS:
                future_price = None
                for offset in range(horizon, horizon + 10):
                    check = signal_date + timedelta(days=offset)
                    if check in price_map:
                        future_price = price_map[check]
                        break

                if future_price and signal_price > 0:
                    ret = (future_price - signal_price) / signal_price
                    # H2=看涨, L2=看跌
                    setup_type = setup.setup_type.value
                    if setup_type == "H2":
                        correct = ret > 0
                    else:  # L2 → 看跌
                        correct = ret < 0
                    outcomes[horizon] = {"ret": ret, "correct": correct}

            all_signals.append({
                "symbol": symbol,
                "date": signal_date,
                "setup_type": setup.setup_type.value,
                "quality": float(setup.quality_score),
                "p_rule": round(p_rule, 4),
                "market_state": current_state.state.value,
                "confidence": confidence,
                "outcomes": outcomes,
            })

    # ===== 汇总分析 =====
    print(f"\n总信号: {len(all_signals)} 条")
    h2_sigs = [s for s in all_signals if s["setup_type"] == "H2"]
    l2_sigs = [s for s in all_signals if s["setup_type"] == "L2"]
    print(f"  H2: {len(h2_sigs)}条  L2: {len(l2_sigs)}条")

    # ---- 按期限汇总 ----
    for setup_type, sigs in [("H2", h2_sigs), ("L2", l2_sigs)]:
        if not sigs:
            continue

        print(f"\n{'─'*60}")
        print(f"  [{setup_type}] 前向验证结果 ({len(sigs)}条信号)")
        print(f"{'─'*60}")
        print(f"  {'期限':>5}  {'有效信号':>6}  {'胜率':>8}  {'平均收益':>10}  {'中位收益':>10}")
        print(f"  {'─'*50}")

        for horizon in HORIZONS:
            results = []
            for s in sigs:
                if horizon in s["outcomes"]:
                    results.append(s["outcomes"][horizon])

            if not results:
                continue

            acc = sum(1 for r in results if r["correct"]) / len(results)
            avg_ret = np.mean([r["ret"] for r in results])
            med_ret = np.median([r["ret"] for r in results])

            bar = "█" * int(acc * 20)
            print(f"  {horizon:>4}天  {len(results):>5}    {acc:>7.1%}  "
                  f"{avg_ret:>+9.4f}  {med_ret:>+9.4f}  {bar}")

    # ---- 按概率分桶 (校准质量评估) ----
    all_with_outcomes = [
        s for s in all_signals if 5 in s["outcomes"]
    ]
    if len(all_with_outcomes) >= 10:
        print(f"\n{'─'*60}")
        print(f"  概率分桶校准评估 (5日前向, {len(all_with_outcomes)}条信号)")
        print(f"{'─'*60}")

        # 按p_rule分桶
        probs = [s["p_rule"] for s in all_with_outcomes]
        outcomes = [1 if s["outcomes"][5]["correct"] else 0 for s in all_with_outcomes]

        bins = [0.49, 0.50, 0.51, 0.52, 0.53, 0.99]
        print(f"  {'概率区间':<14} {'信号数':>6} {'预测均值':>8} {'实际胜率':>8} {'偏差':>8}")
        print(f"  {'─'*46}")
        for i in range(len(bins)-1):
            lo, hi = bins[i], bins[i+1]
            bucket = [(p, o) for p, o in zip(probs, outcomes) if lo <= p < hi]
            if not bucket:
                continue
            b_probs, b_outcomes = zip(*bucket)
            pred_mean = np.mean(b_probs)
            actual_wr = np.mean(b_outcomes)
            bias = actual_wr - pred_mean
            flag = " *** 偏差!" if abs(bias) > 0.10 else ""
            print(f"  [{lo:.2f}, {hi:.2f})    {len(bucket):>4}    {pred_mean:>7.3f}  "
                  f"{actual_wr:>7.3f}  {bias:>+7.3f}{flag}")

        # ECE
        cal = CalibrationLayer(n_bins=5)
        ece = cal.compute_ece(probs, outcomes)
        print(f"\n  ECE(Expected Calibration Error): {ece:.4f}")

    # ---- 分ETF汇总 ----
    print(f"\n{'─'*60}")
    print(f"  分ETF一览 (5日前向)")
    print(f"{'─'*60}")
    print(f"  {'ETF':<16} {'H2信号':>6} {'H2胜率':>8} {'L2信号':>6} {'L2胜率':>8}")
    print(f"  {'─'*50}")

    for symbol in SYMBOLS:
        h2_etf = [s for s in h2_sigs if s["symbol"] == symbol and 5 in s["outcomes"]]
        l2_etf = [s for s in l2_sigs if s["symbol"] == symbol and 5 in s["outcomes"]]

        h2_wr = sum(1 for s in h2_etf if s["outcomes"][5]["correct"]) / len(h2_etf) if h2_etf else 0
        l2_wr = sum(1 for s in l2_etf if s["outcomes"][5]["correct"]) / len(l2_etf) if l2_etf else 0

        if h2_etf or l2_etf:
            print(f"  {symbol:<16} {len(h2_etf):>5}  {h2_wr:>7.1%}  "
                  f"{len(l2_etf):>5}  {l2_wr:>7.1%}")

    print(f"\n{'='*70}")

    # 结论
    print(f"\n  结论:")
    h2_5d = [s for s in h2_sigs if 5 in s["outcomes"]]
    l2_5d = [s for s in l2_sigs if 5 in s["outcomes"]]
    if h2_5d:
        h2_5d_wr = sum(1 for s in h2_5d if s["outcomes"][5]["correct"]) / len(h2_5d)
        print(f"  H2 5日胜率: {h2_5d_wr:.1%} (基准52.6%, 样本={len(h2_5d)})")
    if l2_5d:
        l2_5d_wr = sum(1 for s in l2_5d if s["outcomes"][5]["correct"]) / len(l2_5d)
        print(f"  L2 5日胜率: {l2_5d_wr:.1%} (基准50%, 样本={len(l2_5d)})")

    if len(all_with_outcomes) >= 10:
        print(f"  概率分桶偏差: ECE={ece:.4f} "
              f"({'可接受' if ece < 0.10 else '需改进'} — 目标<0.05)")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
