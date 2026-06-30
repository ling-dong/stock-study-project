#!/usr/bin/env python
"""前向验证: 检测每个Setup信号后N天的实际涨跌 → 找出最优预测期限"""
import sys
sys.path.insert(0, ".")
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.pipeline.orchestrator import PipelineOrchestrator
from collections import defaultdict


HORIZONS = [1, 3, 5, 10, 20]  # 预测期限: 1天/3天/5天/10天/20天

async def main():
    print("=" * 70)
    print("  SPAS 前向验证 — H2信号后N天实际涨跌概率")
    print("=" * 70)

    adapter = LocalAdapter(data_dir="data")
    symbols = ["510300.SH", "159825.SZ", "515170.SH", "512010.SH", "512720.SH",
               "515880.SH", "159915.SZ", "510050.SH", "512880.SH", "515050.SH",
               "512480.SH", "159559.SZ", "159611.SZ"]

    all_results = defaultdict(lambda: defaultdict(list))  # {horizon: {symbol: [wins]}}
    summary_rows = []

    for symbol in symbols:
        df = await adapter.get_bars(symbol, "day")
        if df.empty:
            continue

        # 转为bars并确保时间升序
        bars = []
        for _, row in df.iterrows():
            bars.append(BarOHLCV(
                symbol=symbol, timestamp=row["timestamp"],
                timeframe=TimeFrame.DAY,
                open=Decimal(str(round(float(row["open"]), 4))),
                high=Decimal(str(round(float(row["high"]), 4))),
                low=Decimal(str(round(float(row["low"]), 4))),
                close=Decimal(str(round(float(row["close"]), 4))),
                volume=int(float(row["volume"])) if not pd.isna(row["volume"]) else 0,
                data_availability_time=row["timestamp"],
                source=DataSource.LOCAL,
            ))

        # 跑流水线获取Setup信号
        orch = PipelineOrchestrator()
        predictions = orch.run_on_bars(bars)

        if not predictions:
            continue

        # 按时间排序信号
        predictions.sort(key=lambda p: p.timestamp)

        # 建立价格索引: {timestamp: close_price}
        price_map = {}
        for b in bars:
            if isinstance(b.timestamp, datetime):
                price_map[b.timestamp.date()] = float(b.close)

        # 对每个确认态H2信号做前向验证
        for p in predictions:
            if p.setup_type != "H2" or float(p.direction_prob) <= 0:
                continue

            signal_date = p.timestamp.date() if isinstance(p.timestamp, datetime) else p.timestamp
            signal_price = price_map.get(signal_date)
            if signal_price is None:
                continue

            for horizon in HORIZONS:
                future_date = signal_date + timedelta(days=horizon)
                # 跳过周末/假期：找未来最近的交易日
                for offset in range(horizon, horizon + 10):
                    check_date = signal_date + timedelta(days=offset)
                    future_price = price_map.get(check_date)
                    if future_price is not None:
                        break

                if future_price is None or signal_price == 0:
                    continue

                actual_return = (future_price - signal_price) / signal_price
                # H2信号=看涨，实际>0为正确
                is_correct = actual_return > 0
                all_results[horizon][symbol].append({
                    "date": signal_date,
                    "actual_ret": actual_return,
                    "correct": is_correct,
                })

        # 汇总
        for horizon in HORIZONS:
            results = all_results[horizon].get(symbol, [])
            if results:
                acc = sum(1 for r in results if r["correct"]) / len(results)
                avg_ret = np.mean([r["actual_ret"] for r in results])
                summary_rows.append({
                    "symbol": symbol, "horizon": horizon,
                    "signals": len(results), "accuracy": acc, "avg_return": avg_ret,
                })

    # ====== 输出 ======
    if not summary_rows:
        print("\n  无验证数据！请先运行: python scripts/fetch_real_data.py")
        print("  (确保数据重新获取以修复时间排序问题)")
        return

    summary_df = pd.DataFrame(summary_rows)

    # 打印每只ETF的详细结果
    print(f"\n{'ETF':<16} {'期限':>4} {'信号数':>6} {'胜率':>8} {'平均收益':>10}")
    print("-" * 50)
    for symbol in symbols:
        sym_data = summary_df[summary_df["symbol"] == symbol]
        if sym_data.empty:
            continue
        for _, row in sym_data.iterrows():
            bar = "█" * int(row["accuracy"] * 20)
            print(f"  {row['symbol']:<14} {row['horizon']:>3}天  {row['signals']:>4}个  "
                  f"{row['accuracy']:>7.1%}  {row['avg_return']:>+8.4f}  {bar}")

    # ====== 最优预测期限分析 ======
    print(f"\n{'=' * 70}")
    print(f"  最优预测期限分析")
    print(f"{'=' * 70}")

    horizon_stats = summary_df.groupby("horizon").agg(
        total_signals=("signals", "sum"),
        avg_accuracy=("accuracy", "mean"),
        avg_return=("avg_return", "mean"),
    ).round(4)

    print(f"\n  {'期限':>4}  {'总信号':>6}  {'平均胜率':>10}  {'平均收益':>10}  {'评价'}")
    print(f"  {'-'*50}")
    best_horizon = None
    best_score = -999

    for horizon in HORIZONS:
        row = horizon_stats.loc[horizon] if horizon in horizon_stats.index else None
        if row is None or row["total_signals"] == 0:
            continue
        # 综合评分 = 胜率 × 收益 × sqrt(信号数)（信号越多越可靠）
        score = row["avg_accuracy"] * max(row["avg_return"], 0.001) * np.sqrt(row["total_signals"])
        star = ""
        if score > best_score:
            best_score = score
            best_horizon = horizon
            star = " ★ 最优"
        print(f"  {horizon:>3}天  {int(row['total_signals']):>5}    {row['avg_accuracy']:>8.1%}    "
              f"{row['avg_return']:>+8.4f}  {star}")

    # 结论
    print(f"\n  >>> 建议预测期限: {best_horizon}天 <<<")
    print(f"  理由: 在所有期限中综合评分最高（胜率×收益×√信号数）")

    # 全板块汇总
    overall = summary_df.groupby("horizon")["accuracy"].agg(["mean", "std", "count"])
    best_overall = overall["mean"].idxmax()
    print(f"\n  全板块最优: {best_overall}天 (平均胜率 {overall.loc[best_overall, 'mean']:.1%})")

    # 对电力ETF特别说明
    power_data = summary_df[summary_df["symbol"] == "159611.SZ"]
    if not power_data.empty:
        print(f"\n  [电力ETF 159611.SZ]")
        for _, row in power_data.iterrows():
            print(f"    {row['horizon']}天预测: {row['signals']}个信号, "
                  f"胜率{row['accuracy']:.1%}, 平均收益{row['avg_return']:+.4f}")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    asyncio.run(main())
