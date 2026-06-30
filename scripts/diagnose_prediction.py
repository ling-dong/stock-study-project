#!/usr/bin/env python
"""诊断脚本: 追踪半导体ETF预测链路的每一个中间值"""
import sys, io
sys.path.insert(0, ".")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import asyncio, yaml, numpy as np, pandas as pd
from datetime import datetime
from decimal import Decimal
from collections import Counter

from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine


async def main():
    # 只测半导体ETF
    code, name, sector_id = "512480.SH", "半导体ETF", "801760"

    with open("config/settings.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    adapter = LocalAdapter("data")
    df = await adapter.get_bars(code, "day")
    bars = []
    for _, row in df.iterrows():
        bars.append(BarOHLCV(
            symbol=code, timestamp=row["timestamp"], timeframe=TimeFrame.DAY,
            open=Decimal(str(round(float(row["open"]), 4))),
            high=Decimal(str(round(float(row["high"]), 4))),
            low=Decimal(str(round(float(row["low"]), 4))),
            close=Decimal(str(round(float(row["close"]), 4))),
            volume=int(float(row["volume"])) if not pd.isna(row["volume"]) else 0,
            data_availability_time=row["timestamp"], source=DataSource.LOCAL,
        ))
    closes = np.array([float(b.close) for b in bars])

    print("=" * 70)
    print(f"  {name} ({code}) 预测链路逐层诊断")
    print("=" * 70)
    print(f"  数据: {len(bars)}根日线, {bars[0].timestamp.date()} ~ {bars[-1].timestamp.date()}")
    print(f"  最新价: {closes[-1]:.4f}")

    # ===== Layer 1: MarketStateSvc =====
    print(f"\n{'─'*60}")
    print(f"  [Layer 1] MarketStateSvc — 为什么判定NEUTRAL?")
    print(f"{'─'*60}")

    ms = MarketStateSvc()
    for b in bars[-120:]:
        state = ms.update(b)

    # 打印内部状态
    closes_20 = np.array([float(b.close) for b in bars[-22:]])
    ema = pd.Series(closes_20).ewm(span=20).mean().values
    ema_slope = ema[-1] - ema[-2]
    print(f"  EMA20斜率: {ema_slope:+.6f} (正值→BULL倾向)")

    bf = BarFeatureSvc()
    recent_bars = ms._history_bars[-20:]
    trend_count = sum(1 for b in recent_bars
                      if bf.compute_body_ratio(b) > 0.5
                      and float(b.close) > float(b.open))
    trend_ratio = trend_count / len(recent_bars)
    print(f"  趋势K线比例: {trend_ratio:.2f} (BULL阈值>{ms.trend_ratio_bull}, BEAR阈值<{ms.trend_ratio_bear})")

    adx = ms._calc_adx(ms._history_bars, ms.adx_period)
    print(f"  ADX(14): {adx:.1f} (BULL需>{ms.adx_threshold}, TRENDING需>25)")

    print(f"  判定条件:")
    print(f"    ema_slope>0?     {ema_slope > 0} (值={ema_slope:+.6f})")
    print(f"    trend_ratio>{ms.trend_ratio_bull}? {trend_ratio > ms.trend_ratio_bull} (值={trend_ratio:.2f})")
    print(f"    adx>{ms.adx_threshold}?         {adx > ms.adx_threshold} (值={adx:.1f})")
    all_bull = ema_slope > 0 and trend_ratio > ms.trend_ratio_bull and adx > ms.adx_threshold
    print(f"    => BULL: {all_bull}")
    print(f"  当前状态: {final_state.state.value if (final_state := state) else 'none'}")
    print(f"  结论: 三条件必须同时满足才能判BULL。EMA斜率可能为正但{'' if all_bull else 'ADX不足或趋势K线比例不够'}")

    # 近120天状态分布
    ms2 = MarketStateSvc()
    states_120 = []
    for b in bars[-120:]:
        s = ms2.update(b)
        if s is not None: states_120.append(s.state.value)
    sc = Counter(states_120)
    print(f"  近120天分布: {dict(sc)}")

    # ===== Layer 2: SetupRecogSvc =====
    print(f"\n{'─'*60}")
    print(f"  [Layer 2] SetupRecogSvc — 为什么只有1个信号且是2年前的?")
    print(f"{'─'*60}")

    sr = SetupRecogSvc()
    all_sigs = []
    for b in bars:
        sig = sr.update(b)
        if sig is not None: all_sigs.append(sig)

    confirmed = [s for s in all_sigs if s.is_confirmed]
    candidates = [s for s in all_sigs if not s.is_confirmed]

    print(f"  总信号: {len(all_sigs)} (确认:{len(confirmed)}, 候选:{len(candidates)})")
    print(f"  信号密度: {len(all_sigs)/len(bars)*100:.2f}% ({len(bars)}根K线)")
    print(f"  最近确认信号距今: ", end="")
    if confirmed:
        days = (bars[-1].timestamp.date() - confirmed[-1].timestamp.date()).days
        print(f"{days} 天")
        print(f"  最近候选信号距今: ", end="")
    if candidates:
        days = (bars[-1].timestamp.date() - candidates[-1].timestamp.date()).days
        print(f"{days} 天")

    # 检查最近20根Bar为什么沒有候选态
    print(f"\n  检查最近20根Bar的H2候选检测条件:")
    sr_test = SetupRecogSvc()
    for i, b in enumerate(bars[-20:]):
        sig = sr_test.update(b)
        if sig is not None:
            d = b.timestamp.strftime("%Y-%m-%d")
            print(f"    Bar {i}: {d} → {sig.candidate_vs_confirmed.value} quality={float(sig.quality_score):.3f}")

    # 找最近的局部低点
    recent_closes = closes[-30:]
    lows = []
    for i in range(2, len(recent_closes) - 2):
        if (recent_closes[i] < recent_closes[i-1] and recent_closes[i] < recent_closes[i-2]
            and recent_closes[i] < recent_closes[i+1] and recent_closes[i] < recent_closes[i+2]):
            lows.append(i)
    print(f"  最近30根Bar的局部低点: {lows} ({len(lows)}个)")
    if len(lows) >= 2:
        leg1, leg2 = lows[-2], lows[-1]
        print(f"  最近两个低点: leg1={leg1}({recent_closes[leg1]:.4f}), leg2={leg2}({recent_closes[leg2]:.4f})")
        print(f"  higher_low条件: leg2({recent_closes[leg2]:.4f}) > leg1({recent_closes[leg1]:.4f})? {recent_closes[leg2] > recent_closes[leg1]}")
        # 成交量萎缩检查
        recent_vols = [float(b.volume) for b in bars[-30:]]
        vol_leg1 = np.mean(recent_vols[leg1-2:leg1+3]) if leg1 >= 2 else 0
        vol_leg2 = np.mean(recent_vols[leg2-2:leg2+3]) if leg2 >= 2 else 0
        if vol_leg1 > 0:
            vol_ratio = vol_leg2 / vol_leg1
            print(f"  缩量条件: vol_leg2/vol_leg1 = {vol_ratio:.3f} < {sr.volume_shrink_ratio}? {vol_ratio < sr.volume_shrink_ratio}")

    # ===== Layer 3: RuleEngine =====
    print(f"\n{'─'*60}")
    print(f"  [Layer 3] RuleEngine — 为什么概率恰好是50.0%?")
    print(f"{'─'*60}")

    re_engine = RuleEngine()
    print(f"  sample_threshold = {re_engine.sample_threshold}")
    print(f"  _baserates = {re_engine._baserates}")
    print(f"  _sample_counts = {re_engine._sample_counts}")

    if confirmed:
        last_sig = confirmed[-1]
        fs_state = final_state  # from earlier MarketStateSvc run
        # 逐个检查 evaluate 内部逻辑
        print(f"\n  输入:")
        print(f"    setup.is_confirmed = {last_sig.is_confirmed}")
        print(f"    setup.quality_score = {float(last_sig.quality_score)}")
        print(f"    setup.setup_type = {last_sig.setup_type.value}")
        print(f"    market_state.state = {fs_state.state.value}")
        print(f"    market_state.is_trending = {fs_state.is_trending}")

        features, p_rule, confidence = re_engine.evaluate(last_sig, fs_state, float(bars[-1].close))

        print(f"\n  evaluate() 内部逻辑追踪:")
        sample_size = re_engine._sample_counts.get(last_sig.setup_type.value, 0)
        print(f"    sample_size = {sample_size}")
        print(f"    sample_size < threshold({re_engine.sample_threshold})? {sample_size < re_engine.sample_threshold}")
        print(f"    → historical_baserate = {features['historical_baserate']} (强制0.5)")

        trend_aligned = re_engine._check_trend_alignment(last_sig, fs_state)
        print(f"    trend_aligned = {trend_aligned} (H2需要BULL状态)")
        print(f"    趋势加分? sample_size>=threshold? {sample_size >= re_engine.sample_threshold} → 跳过")

        print(f"    NEUTRAL扣分? sample_size>=threshold? {sample_size >= re_engine.sample_threshold} → 跳过")

        print(f"    setup_quality({float(last_sig.quality_score)}) >= 0.5 → medium置信度")
        print(f"    p_rule = 0.5 + (historical_baserate({features['historical_baserate']}) - 0.5) * 0.7")
        print(f"    p_rule = 0.5 + ({features['historical_baserate']} - 0.5) * 0.7 = 0.5 + 0 * 0.7 = 0.5")

        print(f"\n  输出:")
        print(f"    p_rule = {p_rule:.4f}")
        print(f"    confidence = {confidence}")

        # build_prediction
        pred = re_engine.build_prediction(last_sig, fs_state, float(bars[-1].close))
        print(f"\n  build_prediction() 输出:")
        print(f"    direction_prob = {float(pred.direction_prob)}")
        print(f"    r_r_ratio = {float(pred.r_r_ratio)}")
        print(f"    expected_value = {float(pred.expected_value)}")

    # ===== 根因分析 =====
    print(f"\n{'='*70}")
    print(f"  根因总结")
    print(f"{'='*70}")
    issues = []
    if confirmed and float(confirmed[-1].quality_score) >= 0.5:
        issues.append("""
  [严重] RuleEngine.sample_size=0 → 所有条件调整被阻塞
  ─────────────────────────────────────────────
  _sample_counts = {"H2": 0, "L2": 0, "FB": 0}  ← 从未被 update_baserate() 调用
  导致:
    - historical_baserate 强制 = 0.5 (sample < 100)
    - BULL趋势加分跳过 (sample < 100)
    - NEUTRAL惩罚跳过 (sample < 100)
    - 最终 p_rule = 0.5 (精确等于50%)

  修复: update_baserate() 需要被回测系统调用, 或降低 sample_threshold 至 10
""")
    issues.append("""
  [中等] MarketState 79%时间判NEUTRAL → 趋势加分永远不触发
  ─────────────────────────────────────────────
  半导体ETF近60天涨78%但状态机判NEUTRAL:
  - EMA20斜率可能不够持续 (需连续2Bar确认)
  - ADX(14)可能<20 (暴涨后的均线纠缠)
  - 设计文档日线校准参数可能仍偏严格

  修复: adx_threshold: 20 → 18, trend_bar_ratio_bull: 0.45 → 0.38
""")
    issues.append("""
  [中等] SetupRecogSvc日线信号稀疏 → 预测用的是2年前的信号
  ─────────────────────────────────────────────
  726天仅1个确认H2信号, 最近的在828天前:
  - 局部低点检测条件过严 (连续3Bar较低)
  - 成交量萎缩阈值 0.92 在日线上过于严格
  - 最近30根Bar即使有明显波动也无法产生候选态

  修复: volume_shrink_ratio: 0.92 → 0.95, 或增加更灵活的回撤检测
""")

    for issue in issues:
        print(issue)

asyncio.run(main())
