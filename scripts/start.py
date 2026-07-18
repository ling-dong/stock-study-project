#!/usr/bin/env python
"""SPAS 一键启动脚本 — 获取真实数据 → 运行流水线 → 启动API服务"""
import sys
sys.path.insert(0, ".")
import asyncio
import argparse


async def cmd_fetch(args):
    """Step 1: 获取真实数据"""
    from scripts.fetch_real_data import main
    await main()


async def cmd_pipeline(args):
    """Step 2: 运行流水线"""
    from scripts.run_pipeline import main
    await main()


async def cmd_backtest(args):
    """Step 3: 运行回测"""
    from scripts.run_backtest import main
    await main()


def cmd_serve(args):
    """Step 4: 启动API服务"""
    import uvicorn
    from src.signals.service import SPASService
    from src.signals.api import create_app

    print("=" * 60)
    print("  SPAS API Server — http://127.0.0.1:8000")
    print("  Endpoints:")
    print("    GET /api/spas/signal/{code}          — 运行 SPAS 流水线")
    print("    GET /api/spas/market/etfs            — ETF 列表")
    print("    GET /api/spas/market/etf/{code}/ohlcv — OHLCV 数据")
    print("    GET /api/spas/system/status          — 系统状态")
    print("=" * 60)

    service = SPASService()
    app = create_app(service)
    uvicorn.run(app, host="127.0.0.1", port=8000)


async def cmd_all(args):
    """一键运行: 数据 → 流水线 → API"""
    print("[1/3] 获取真实数据...")
    await cmd_fetch(args)

    print("\n[2/3] 运行流水线...")
    await cmd_pipeline(args)

    print("\n[3/3] 启动API服务...")
    cmd_serve(args)


def main():
    parser = argparse.ArgumentParser(
        description="SPAS 股市板块涨跌概率分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/start.py fetch         # 从Tushare获取真实数据
  python scripts/start.py pipeline      # 运行信号分析流水线
  python scripts/start.py backtest      # 运行Walk-Forward回测
  python scripts/start.py serve         # 启动API服务
  python scripts/start.py all           # 一键运行全部
        """,
    )
    parser.add_argument(
        "command",
        choices=["fetch", "pipeline", "backtest", "serve", "all"],
        help="执行命令",
    )

    args = parser.parse_args()

    commands = {
        "fetch": cmd_fetch,
        "pipeline": cmd_pipeline,
        "backtest": cmd_backtest,
        "serve": cmd_serve,
        "all": cmd_all,
    }

    handler = commands[args.command]
    if asyncio.iscoroutinefunction(handler):
        asyncio.run(handler(args))
    else:
        handler(args)


if __name__ == "__main__":
    main()
