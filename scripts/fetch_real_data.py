#!/usr/bin/env python
"""从Tushare Pro获取真实A股ETF行情数据并保存为Parquet"""
import sys
sys.path.insert(0, ".")
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.local import LocalAdapter

TOKEN = "47dc072de82440ad88a57bb0215afd42"
API_URL = "https://ts.gyzcloud.top/api"

ETF_LIST = [
    # 宽基
    ("510300.SH", "沪深300ETF"),
    ("159915.SZ", "创业板ETF"),
    ("510050.SH", "上证50ETF"),
    # 行业
    ("159825.SZ", "农林牧渔ETF"),
    ("515170.SH", "食品饮料ETF"),
    ("512010.SH", "医药ETF"),
    ("512720.SH", "计算机ETF"),
    ("515880.SH", "通信ETF"),
    ("512880.SH", "证券ETF"),
    ("515050.SH", "5GETF"),
    # 用户指定
    ("512480.SH", "半导体ETF"), 
    ("159559.SZ", "存储芯片ETF"),
    ("159611.SZ", "电力ETF"),
    ("515220.SH", "煤炭ETF"),
]


async def main():
    print("=" * 60)
    print("  SPAS 真实数据获取 — Tushare Pro")
    print("=" * 60)

    tushare = TushareAdapter(token=TOKEN, api_url=API_URL)
    local = LocalAdapter(data_dir="data")

    # 1. 连接测试
    print("\n[连接测试] 验证Tushare API连通性...")
    healthy = await tushare.health_check()
    if not healthy:
        print("  FAIL: API连接失败，请检查token和网络")
        return
    print("  OK: API连接正常")

    # 2. 诊断: 直接测试 fund_daily vs daily 接口
    print("\n[诊断] 测试ETF数据接口...")
    try:
        pro = tushare._pro
        # 测试 fund_daily
        df_fund = pro.fund_daily(ts_code='510300.SH', start_date='20260620', end_date='20260625',
                                 fields='ts_code,trade_date,open,high,low,close,vol')
        print(f"  fund_daily(510300.SH): type={type(df_fund).__name__}, "
              f"empty={df_fund.empty if hasattr(df_fund, 'empty') else 'N/A'}, "
              f"len={len(df_fund) if hasattr(df_fund, '__len__') else 'N/A'}")
        if hasattr(df_fund, 'head') and not df_fund.empty:
            print(f"    columns: {list(df_fund.columns)}")
            print(f"    sample:\n{df_fund.head(2)}")

        # 测试 daily (股票)
        df_stock = pro.daily(ts_code='000001.SZ', start_date='20260620', end_date='20260625')
        print(f"  daily(000001.SZ): type={type(df_stock).__name__}, "
              f"empty={df_stock.empty if hasattr(df_stock, 'empty') else 'N/A'}, "
              f"len={len(df_stock) if hasattr(df_stock, '__len__') else 'N/A'}")
        if hasattr(df_stock, 'head') and not df_stock.empty:
            print(f"    columns: {list(df_stock.columns)}")

        # 测试 daily (ETF — 应该失败)
        df_daily_etf = pro.daily(ts_code='510300.SH', start_date='20260620', end_date='20260625')
        print(f"  daily(510300.SH): type={type(df_daily_etf).__name__}, "
              f"empty={df_daily_etf.empty if hasattr(df_daily_etf, 'empty') else 'N/A'}, "
              f"len={len(df_daily_etf) if hasattr(df_daily_etf, '__len__') else 'N/A'}")
    except Exception as e:
        print(f"  诊断ERROR: {e}")

    # 3. 获取日线数据
    start_date = datetime.now() - timedelta(days=365 * 3)  # 3年历史
    end_date = datetime.now() - timedelta(days=1)

    total_bars = 0
    for code, name in ETF_LIST:
        print(f"\n[{name}] {code} 日线数据...")
        try:
            df = await tushare.get_bars(code, "day", start_date, end_date)
            if df.empty:
                print(f"  SKIP: 无数据返回")
                continue

            await local.save_bars(code, "day", df)
            print(f"  OK: {len(df)} 条日线数据已保存")
            total_bars += len(df)

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 60}")
    print(f"  数据获取完成: {total_bars} 条日线记录")
    print(f"  文件保存在 data/ 目录")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
