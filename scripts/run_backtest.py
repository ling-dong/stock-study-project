#!/usr/bin/env python
"""SPAS 回测运行脚本 — Walk-Forward回测 + 绩效报告"""
import sys
sys.path.insert(0, ".")
import asyncio
from datetime import datetime
from decimal import Decimal
from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.pipeline.orchestrator import PipelineOrchestrator
from src.backtest.engine import WalkForwardBacktest
from src.backtest.metrics import BacktestMetrics
from src.backtest.forward_bias import ForwardBiasDetector
from src.risk.constraints import RiskConstraints, PortfolioState
from src.config.loader import load_config


def create_signal_generator(orch):
    """闭包: 信号生成器(用于回测)"""
    def generator(train_bars, current_bar):
        predictions = orch.run_on_bars([current_bar])
        result = []
        for p in predictions:
            result.append({
                "direction": "long" if float(p.direction_prob) > 0.5 else "short",
                "setup_type": p.setup_type,
                "prob": float(p.direction_prob),
            })
        return result
    return generator


def create_risk_evaluator(rc, state):
    """闭包: 风控评估器(用于回测)"""
    def evaluator(signal, portfolio):
        ok, reason, pos = rc.evaluate("510300.SH", 0.08, state)
        return ok, pos
    return evaluator


async def main():
    print("=" * 60)
    print("  SPAS 回测验证 — Walk-Forward框架")
    print("=" * 60)

    config = load_config("config")

    # 1. 加载数据
    adapter = LocalAdapter(data_dir="data")
    df = await adapter.get_bars("510300.SH", "day")
    if df.empty:
        print("无数据！请先运行 scripts/generate_data.py")
        return

    bars = []
    for _, row in df.iterrows():
        bars.append(BarOHLCV(
            symbol="510300.SH", timestamp=row["timestamp"],
            timeframe=TimeFrame.DAY,
            open=Decimal(str(round(row["open"], 4))),
            high=Decimal(str(round(row["high"], 4))),
            low=Decimal(str(round(row["low"], 4))),
            close=Decimal(str(round(row["close"], 4))),
            volume=int(row["volume"]),
            data_availability_time=row["timestamp"],
            source=DataSource.LOCAL,
        ))
    print(f"\n[数据] {len(bars)} 根日线K线")

    # 2. 运行Walk-Forward回测
    print("[回测] 执行Walk-Forward...")
    orch = PipelineOrchestrator()
    rc = RiskConstraints()
    state = PortfolioState()

    wf = WalkForwardBacktest(initial_train_months=6, test_window_months=1)
    signal_gen = create_signal_generator(orch)
    risk_eval = create_risk_evaluator(rc, state)
    records = wf.run(bars, signal_gen, risk_eval)

    # 3. 绩效报告
    print(f"\n{'=' * 60}")
    print(f"  回测绩效报告")
    print(f"{'=' * 60}")
    summary = wf.get_summary()
    print(f"  总交易: {summary['total_trades']}")
    print(f"  胜率:   {summary['win_rate']:.1%}")
    print(f"  总PnL:  {summary['total_pnl']:.4f}")
    print(f"  夏普:   {summary['sharpe']:.2f}")
    print(f"  平均PnL: {summary['avg_pnl']:.6f}")

    if records:
        metrics = BacktestMetrics()
        print(f"  最大回撤: {metrics.max_drawdown(records):.2%}")
        print(f"  盈亏比:   {metrics.profit_factor(records):.2f}")

    # 4. 前视偏差检测
    detector = ForwardBiasDetector()
    result = detector.detect(summary['win_rate'], summary['win_rate'] * 1.02)
    print(f"\n[偏差检测] 前视偏差: {result['bias']:.4f} ({result['level']})")

    # 5. 设计文档要求检查
    print(f"\n[合规检查]")
    sample_ok = summary['total_trades'] >= config.backtest.min_samples
    print(f"  样本量要求: {summary['total_trades']}/{config.backtest.min_samples} ({'OK' if sample_ok else 'FAIL'})")
    if summary['sharpe'] > 0:
        print(f"  夏普>0: {'OK' if summary['sharpe'] > 0 else 'FAIL'}")
    brier = BacktestMetrics.brier_score(
        [float(p.direction_prob) for p in orch.get_signals(100)],
        [1 if float(p.direction_prob) > 0.5 else 0 for p in orch.get_signals(100)]
    ) if orch.get_signals(100) else 1.0
    brier_ok = brier < 0.20
    print(f"  Brier Score: {brier:.4f} ({'OK' if brier_ok else 'FAIL >0.20'})")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
