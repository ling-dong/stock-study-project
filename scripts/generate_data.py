#!/usr/bin/env python
"""生成合成历史数据并保存为Parquet格式，供LocalAdapter使用"""
import sys
sys.path.insert(0, ".")
import pandas as pd
from tests.fixtures.sample_data import generate_bars, generate_swing_bars
from src.data.adapters.local import LocalAdapter
import asyncio


async def main():
    adapter = LocalAdapter(data_dir="data")
    sectors = [
        ("510300.SH", "沪深300ETF"),
        ("159825.SZ", "农林牧渔ETF"),
        ("515170.SH", "食品饮料ETF"),
        ("512010.SH", "医药ETF"),
        ("512720.SH", "计算机ETF"),
        ("515880.SH", "通信ETF"),
    ]

    for code, name in sectors:
        print(f"生成 {name}({code}) 历史数据...")

        # 分钟级数据(60天, 每天48根5分钟K线)
        bars_5min = generate_bars(symbol=code, n_bars=48 * 60, volatility=0.003, trend=0.0001, seed=hash(code) % 10000)
        df_5min = pd.DataFrame([{
            "timestamp": b.timestamp, "open": float(b.open), "high": float(b.high),
            "low": float(b.low), "close": float(b.close), "volume": b.volume, "factor": 1.0,
        } for b in bars_5min])
        await adapter.save_bars(code, "5min", df_5min)

        # 日线数据(2年, 约500个交易日)
        bars_day = generate_bars(symbol=code, n_bars=500, volatility=0.015, trend=0.0005, seed=hash(code) % 10000)
        df_day = pd.DataFrame([{
            "timestamp": b.timestamp, "open": float(b.open), "high": float(b.high),
            "low": float(b.low), "close": float(b.close), "volume": b.volume, "factor": 1.0,
        } for b in bars_day])
        await adapter.save_bars(code, "day", df_day)

        print(f"  → 5min: {len(df_5min)}根, day: {len(df_day)}根")

    print(f"\n全部数据已保存到 data/ 目录")
    print(f"总文件: {len(sectors) * 2} 个 Parquet 文件")


if __name__ == "__main__":
    asyncio.run(main())
