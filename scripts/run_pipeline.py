#!/usr/bin/env python
"""SPAS 主运行脚本 — 加载数据 → 运行流水线 → 输出信号"""
import sys
sys.path.insert(0, ".")
import asyncio
import pandas as pd
from datetime import datetime
from src.data.adapters.local import LocalAdapter
from src.data.fetcher import DataFetcher
from src.pipeline.orchestrator import PipelineOrchestrator
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from decimal import Decimal
from src.risk.constraints import RiskConstraints, PortfolioState
from src.config.loader import load_config


async def main():
    print("=" * 60)
    print("  SPAS 股市板块涨跌概率分析系统 V0.1")
    print("=" * 60)

    # 1. 加载配置
    config = load_config("config")
    print(f"\n[配置] 风控阈值: 日{config.risk_constraints.L1_daily_stop:.0%} "
          f"周{config.risk_constraints.L2_weekly_stop:.0%} "
          f"月{config.risk_constraints.L3_monthly_stop:.0%} "
          f"最大回撤{config.risk_constraints.L4_max_drawdown:.0%}")

    # 2. 加载数据
    print("\n[数据] 加载本地Parquet数据...")
    adapter = LocalAdapter(data_dir="data")
    symbols = ["510300.SH", "159825.SZ", "515170.SH", "512010.SH", "512720.SH", "515880.SH"]

    all_predictions = []
    for symbol in symbols:
        df = await adapter.get_bars(symbol, "5min")
        if df.empty:
            print(f"  {symbol}: 无数据，跳过")
            continue

        print(f"  {symbol}: {len(df)} 根K线")

        # 转换为BarOHLCV列表
        bars = []
        for _, row in df.tail(200).iterrows():  # 取最近200根
            bar = BarOHLCV(
                symbol=symbol, timestamp=row["timestamp"],
                timeframe=TimeFrame.M5,
                open=Decimal(str(round(row["open"], 4))),
                high=Decimal(str(round(row["high"], 4))),
                low=Decimal(str(round(row["low"], 4))),
                close=Decimal(str(round(row["close"], 4))),
                volume=int(row["volume"]),
                data_availability_time=row["timestamp"],
                source=DataSource.LOCAL,
            )
            bars.append(bar)

        # 3. 运行流水线
        orch = PipelineOrchestrator()
        predictions = orch.run_on_bars(bars)

        if predictions:
            print(f"    → 产出 {len(predictions)} 个信号")
            for p in predictions[-3:]:  # 最近3个
                print(f"      [{p.setup_type}] dir={float(p.direction_prob):.3f} "
                      f"rrr={float(p.r_r_ratio):.2f} conf={p.confidence_level}")
            all_predictions.extend(predictions)
        else:
            print(f"    → 无信号")

    # 4. 风控评估
    print(f"\n[风控] 六层约束检查...")
    rc = RiskConstraints()
    state = PortfolioState()
    for p in all_predictions[-10:]:
        ok, reason, pos = rc.evaluate(p.symbol, 0.08, state)
        status = "PASS" if ok else "BLOCK"
        print(f"  [{status}] {p.symbol} {p.setup_type}: {reason} (pos={pos:.2%})")

    # 5. 汇总
    print(f"\n{'=' * 60}")
    print(f"  运行完成: {len(symbols)} 个标的, {len(all_predictions)} 个信号")
    if all_predictions:
        avg_prob = sum(float(p.direction_prob) for p in all_predictions) / len(all_predictions)
        h2_count = sum(1 for p in all_predictions if p.setup_type == "H2")
        print(f"  平均方向概率: {avg_prob:.3f}, H2信号: {h2_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
