#!/usr/bin/env python
"""SPAS 预测脚本 — 指定ETF的完整预测分析"""
import sys
sys.path.insert(0, ".")
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.risk.constraints import RiskConstraints, PortfolioState, kelly_position
from src.risk.volatility import VolatilityAnchor
from src.backtest.cost_model import CostModel
from src.config.loader import load_config


async def predict_etf(code, name, config):
    adapter = LocalAdapter(data_dir="data")
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
    daily_ret = np.diff(closes) / closes[:-1]
    dates = [b.timestamp.strftime("%Y-%m-%d") for b in bars]
    latest = bars[-1]

    print(f"\n{'='*65}")
    print(f"  {name} ({code}) 预测分析")
    print(f"{'='*65}")

    # [1] 市场状况
    vol_5 = np.std(daily_ret[-5:]) * np.sqrt(252) * 100 if len(daily_ret) >= 5 else 0
    vol_20 = np.std(daily_ret[-20:]) * np.sqrt(252) * 100 if len(daily_ret) >= 20 else 0
    ret_5 = (closes[-1] / closes[-6] - 1) * 100 if len(closes) >= 6 else 0
    ret_20 = (closes[-1] / closes[-21] - 1) * 100 if len(closes) >= 21 else 0
    ms = MarketStateSvc(confirmation_bars=1)
    fs = None
    for b in bars:
        s = ms.update(b)
        if s is not None:
            fs = s

    state_map = {"bull": "BULL", "bear": "BEAR", "neutral": "NEUTRAL"}
    trend_icon = state_map.get(fs.state.value, "?")
    print(f"  最新交易日: {dates[-1]}  收盘价: {float(latest.close):.4f}")
    print(f"  5日涨跌: {ret_5:+.2f}%  20日涨跌: {ret_20:+.2f}%")
    print(f"  波动率: 5日{vol_5:.1f}% / 20日{vol_20:.1f}%")
    print(f"  市场状态: {trend_icon}  置信度: {float(fs.confidence):.2f}  持续: {fs.duration}天")

    # [2] Setup 扫描
    sr = SetupRecogSvc()
    bf = BarFeatureSvc()
    all_sigs = []
    for b in bars:
        sig = sr.update(b)
        if sig is not None:
            all_sigs.append(sig)

    confirmed = [s for s in all_sigs if s.is_confirmed]
    candidates = [s for s in all_sigs if not s.is_confirmed]

    print(f"\n  [Setup扫描] 确认态: {len(confirmed)}个  候选态(未确认): {len(candidates)}个")
    if confirmed:
        print(f"  {'日期':<14} {'类型':<6} {'状态':<12} {'质量':>6} {'成熟度':>6}")
        print(f"  {'-'*44}")
        for s in confirmed[-5:]:
            d = s.timestamp.strftime("%Y-%m-%d")
            print(f"  {d:<14} {s.setup_type.value:<6} {'CONFIRMED':<12} {float(s.quality_score):>6.3f} {s.maturity:>5}")

    if candidates:
        print(f"\n  候选态(未确认)及拒绝原因:")
        for s in candidates[-5:]:
            d = s.timestamp.strftime("%Y-%m-%d")
            bar_idx = next((i for i, b_ in enumerate(bars) if b_.timestamp.strftime("%Y-%m-%d") == d), None)
            issues = []
            if bar_idx:
                bb = bars[bar_idx]
                br = bf.compute_body_ratio(bb)
                if br < 0.5:
                    issues.append(f"实体比{br:.2f}<0.5")
                if fs.state.value != "bull":
                    issues.append("非BULL趋势")
                recent_vols = [float(b.volume) for b in bars[max(0, bar_idx-6):bar_idx]]
                avg_vol = np.mean(recent_vols) if recent_vols else float(bb.volume)
                vol_ratio = float(bb.volume) / avg_vol if avg_vol > 0 else 0
                if vol_ratio < 1.2:
                    issues.append(f"量比{vol_ratio:.1f}<1.2")
            print(f"    {d}  quality={float(s.quality_score):.3f}  " + ("; ".join(issues) if issues else "条件满足"))

    # [3] 预测
    print(f"\n  [5日预测] (最优期限, 基准胜率52.6%)")
    horizon = config.prediction_horizon_optimal_days
    re_engine = RuleEngine()
    cm = CostModel()

    if confirmed:
        last_sig = confirmed[-1]
        pred = re_engine.build_prediction(last_sig, fs, float(latest.close))
        ev = cm.expected_value(
            float(pred.direction_prob), 1 - float(pred.direction_prob), 0.10,
            float(latest.close) * 0.053, -float(latest.close) * 0.025, float(latest.close),
        )
        k_pos = kelly_position(float(pred.direction_prob), float(pred.r_r_ratio))
        days_ago = (bars[-1].timestamp - last_sig.timestamp).days
        direction = "看涨" if float(pred.direction_prob) > 0.5 else "看跌"

        print(f"  信号触发日: {last_sig.timestamp.strftime('%Y-%m-%d')} (距今{days_ago}天)")
        print(f"  方向概率:   {float(pred.direction_prob)*100:.1f}% ({direction})")
        print(f"  目标达成率: {float(pred.target_prob)*100:.1f}%  止损率: {float(pred.stop_prob)*100:.1f}%")
        print(f"  风险回报比: {float(pred.r_r_ratio):.2f}")
        print(f"  5日期望收益: {ev*100:+.3f}% (含佣金/印花税/滑点)")
        print(f"  凯利仓位:   {k_pos*100:.2f}% (1/4 Kelly)")
        print(f"  置信度:     {pred.confidence_level}")
    else:
        print(f"  当前无确认态H2信号")
        k_pos = kelly_position(0.526, 2.0)
        print(f"  基准概率:   52.6% (全板块34个H2信号5日前向验证)")
        print(f"  凯利仓位:   {k_pos*100:.2f}%")

    # 关注最新候选
    if candidates:
        latest_cand = candidates[-1]
        cd = latest_cand.timestamp.strftime("%Y-%m-%d")
        days_ago = (bars[-1].timestamp - latest_cand.timestamp).days
        print(f"\n  [关注] 最近候选态: {cd} (距今{days_ago}天)")
        print(f"    Setup类型: {latest_cand.setup_type.value}  质量评分: {float(latest_cand.quality_score):.3f}")
        print(f"    需满足条件: 突破Bar实体>0.5 + 成交量放大x1.2 + 价格突破H2极点")

    # [4] 风控
    rc = RiskConstraints()
    ok, reason, pos = rc.evaluate(code, 0.08, PortfolioState())
    va = VolatilityAnchor()
    if len(daily_ret) >= 20:
        scaled = va.scale_position(list(daily_ret[-20:]), list(daily_ret[-5:]), 0.08)
    else:
        scaled = 0.08

    print(f"\n  [风控] 六层约束: {'ALL PASS' if ok else reason}")
    print(f"  波动率锚定仓位: {scaled*100:.2f}% (基础8%)")

    return {
        "name": name, "code": code, "close": float(latest.close),
        "ret_5": ret_5, "ret_20": ret_20, "vol_20": vol_20,
        "state": fs.state.value, "state_conf": float(fs.confidence),
        "confirmed": len(confirmed), "candidates": len(candidates),
        "last_confirmed_date": confirmed[-1].timestamp.strftime("%Y-%m-%d") if confirmed else "N/A",
        "last_candidate_date": candidates[-1].timestamp.strftime("%Y-%m-%d") if candidates else "N/A",
    }


async def main():
    config = load_config("config")
    results = []
    for code, name in [("512480.SH", "半导体ETF"), ("515880.SH", "通信ETF")]:
        r = await predict_etf(code, name, config)
        results.append(r)

    # 对比总结
    print(f"\n{'='*65}")
    print(f"  对比总结")
    print(f"{'='*65}")
    print(f"  {'指标':<18} {'半导体ETF (512480)':>22} {'通信ETF (515880)':>22}")
    print(f"  {'-'*62}")
    rows = [
        ("最新价", "close", "{:.4f}"),
        ("5日涨跌", "ret_5", "{:+.2f}%"),
        ("20日涨跌", "ret_20", "{:+.2f}%"),
        ("波动率(20日)", "vol_20", "{:.1f}%"),
        ("市场状态", "state", "{}"),
        ("状态置信度", "state_conf", "{:.2f}"),
        ("H2确认数", "confirmed", "{}"),
        ("候选态数", "candidates", "{}"),
        ("最后信号日", "last_confirmed_date", "{}"),
    ]
    for label, key, fmt in rows:
        v0 = fmt.format(results[0].get(key, "N/A"))
        v1 = fmt.format(results[1].get(key, "N/A"))
        print(f"  {label:<18} {v0:>22} {v1:>22}")

    # 推荐
    print(f"\n  >>> 推荐 <<<")
    for r in results:
        score = r["confirmed"] + (1 if r["state"] == "bull" else 0) + (1 if r["ret_5"] > 0 else 0)
        if score >= 3:
            rec = "优先关注"
        elif score >= 1:
            rec = "可观察"
        else:
            rec = "暂观望"
        bull_str = "BULL" if r["state"] == "bull" else "非BULL"
        ret_str = "涨" if r["ret_5"] > 0 else "跌"
        print(f"  {r['name']}: {rec} (评分 {score}/3 = H2确认{r['confirmed']} + {bull_str} + 5日{ret_str})")

    print(f"\n{'='*65}")


if __name__ == "__main__":
    asyncio.run(main())
