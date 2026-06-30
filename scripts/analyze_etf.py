#!/usr/bin/env python
"""SPAS ETF深度分析: 可配置标的列表"""
import sys
import io
sys.path.insert(0, ".")
# 强制UTF-8编码，避免GBK错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import asyncio
import yaml
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter

from src.data.adapters.local import LocalAdapter
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.risk.constraints import RiskConstraints, PortfolioState, kelly_position
from src.risk.volatility import VolatilityAnchor
from src.backtest.cost_model import CostModel
from src.sentiment.collector import SentimentCollector
from src.sector_linkage.graph import SectorLinkageGraph

# 配置
with open("config/settings.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

ETF_LIST = [
    ("515050.SH", "通信设备", "801761"),
    ("562590.SH", "半导体材料", "801080"),
    ("159611.SZ", "电力ETF", "801730"),
    ("515220.SH", "煤炭ETF", "801020"),
    ("159869.SZ", "CPO/光通信", "CPO"),
    ("512480.SH", "半导体ETF", "801760"),
]

sentiment = SentimentCollector(
    tushare_token=cfg["tushare"]["token"],
    tushare_api_url=cfg["tushare"]["api_url"],
)
linkage = SectorLinkageGraph.with_defaults()

all_results: dict = {}


async def analyze_etf(code, name, sector_id):
    print()
    print("─" * 70)
    print(f"  ▎{name} ({code})  申万板块: {sector_id}")
    print("─" * 70)

    # ---- 数据加载 ----
    adapter = LocalAdapter("data")
    df = await adapter.get_bars(code, "day")
    bars = []
    for _, row in df.iterrows():
        bars.append(BarOHLCV(
            symbol=code,
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

    closes = np.array([float(b.close) for b in bars])
    daily_ret = np.diff(closes) / closes[:-1]
    dates = [b.timestamp.strftime("%Y-%m-%d") for b in bars]
    latest = bars[-1]

    # ===== 1. 市场状况 (使用config参数) =====
    vol_5 = np.std(daily_ret[-5:]) * np.sqrt(252) * 100 if len(daily_ret) >= 5 else 0
    vol_20 = np.std(daily_ret[-20:]) * np.sqrt(252) * 100 if len(daily_ret) >= 20 else 0
    ret_5 = (closes[-1] / closes[-6] - 1) * 100 if len(closes) >= 6 else 0
    ret_20 = (closes[-1] / closes[-21] - 1) * 100 if len(closes) >= 21 else 0
    ret_60 = (closes[-1] / closes[-61] - 1) * 100 if len(closes) >= 61 else 0

    ms_cfg = cfg.get("market_state", {})
    ms = MarketStateSvc(
        ema_period=ms_cfg.get("ema_period", 20),
        adx_period=ms_cfg.get("adx_period", 14),
        adx_threshold=ms_cfg.get("adx_threshold", 20),
        trend_ratio_bull=ms_cfg.get("trend_bar_ratio_bull", 0.45),
        trend_ratio_bear=ms_cfg.get("trend_bar_ratio_bear", 0.35),
        confirmation_bars=ms_cfg.get("confirmation_bars", 2),
        initial_confidence=ms_cfg.get("initial_confidence", 0.3),
        confidence_per_bar=ms_cfg.get("confidence_per_bar", 0.05),
        max_confidence=ms_cfg.get("max_confidence", 0.9),
    )
    final_state = None
    state_history = []
    for b in bars[-120:]:
        s = ms.update(b)
        if s is not None:
            final_state = s
            state_history.append(s.state.value)

    state_counts = Counter(state_history)
    bull_pct = (
        state_counts.get("bull", 0) / len(state_history) * 100
        if state_history else 0
    )

    state_icon = {"bull": "BULL", "bear": "BEAR", "neutral": "NEUTRAL"}
    print(f"  最新价: {float(latest.close):.4f}  |  {dates[-1]}")
    print(f"  涨跌:   5日{ret_5:+.2f}%  20日{ret_20:+.2f}%  60日{ret_60:+.2f}%")
    print(f"  波动率: 5日{vol_5:.1f}%  20日{vol_20:.1f}%")
    if final_state:
        st = state_icon.get(final_state.state.value, "?")
        print(f"  市场状态: {st}  置信度={float(final_state.confidence):.2f}  持续{final_state.duration}天")
    bear_pct = state_counts.get("bear", 0) / len(state_history) * 100 if state_history else 0
    neutral_pct = state_counts.get("neutral", 0) / len(state_history) * 100 if state_history else 0
    print(f"  近120日状态分布: BULL={bull_pct:.0f}%  BEAR={bear_pct:.0f}%  NEUTRAL={neutral_pct:.0f}%")

    # ===== 2. Setup 扫描 =====
    bf = BarFeatureSvc()
    # Setup识别 (使用config参数)
    setup_cfg = cfg.get("setup", {})
    sr = SetupRecogSvc(
        volume_shrink_ratio=setup_cfg.get("volume_shrink_ratio", 0.92),
        breakout_volume_multiplier=setup_cfg.get("breakout_volume_multiplier", 1.05),
        breakout_body_ratio=setup_cfg.get("breakout_body_ratio", 0.30),
    )
    all_sigs = []
    for b in bars:
        sig = sr.update(b)
        if sig is not None:
            all_sigs.append(sig)

    confirmed = [s for s in all_sigs if s.is_confirmed]
    candidates = [s for s in all_sigs if not s.is_confirmed]

    print(f"\n  [Setup扫描] 确认态: {len(confirmed)}个  候选态: {len(candidates)}个")

    if confirmed:
        print(f"  {'日期':<14} {'类型':<6} {'质量':>6} {'成熟度':>5}  {'距今':>5}")
        print(f"  {'─'*40}")
        for s in confirmed[-8:]:
            d = s.timestamp.strftime("%Y-%m-%d")
            days_ago = (bars[-1].timestamp.date() - s.timestamp.date()).days
            print(f"  {d:<14} {s.setup_type.value:<6} {float(s.quality_score):>6.3f} {s.maturity:>4}  {days_ago:>4}d")

    if candidates:
        print(f"\n  [候选态 — 未确认原因]")
        for s in candidates[-3:]:
            d = s.timestamp.strftime("%Y-%m-%d")
            issues = []
            for i, b_ in enumerate(bars):
                if b_.timestamp.strftime("%Y-%m-%d") == d:
                    br = bf.compute_body_ratio(b_)
                    if br < 0.5:
                        issues.append(f"实体比{br:.2f}<0.5")
                    if final_state and final_state.state.value != "bull":
                        issues.append("非BULL趋势")
                    recent_vols = [float(bv.volume) for bv in bars[max(0, i-6):i]]
                    avg_vol = np.mean(recent_vols) if recent_vols else float(b_.volume)
                    vol_ratio = float(b_.volume) / avg_vol if avg_vol > 0 else 0
                    if vol_ratio < 1.2:
                        issues.append(f"量比{vol_ratio:.1f}<1.2")
                    break
            print(f"    {d}  quality={float(s.quality_score):.3f}  "
                  + ("; ".join(issues) if issues else "等待后续确认"))

    # ===== 3. 预测 =====
    horizon = cfg["prediction_horizon"]["optimal_days"]
    re_engine = RuleEngine()
    cm = CostModel()

    # 分Setup类型取最近信号
    h2_confirmed = [s for s in all_sigs if s.setup_type.value == "H2" and s.is_confirmed]
    l2_confirmed = [s for s in all_sigs if s.setup_type.value == "L2" and s.is_confirmed]
    last_h2 = h2_confirmed[-1] if h2_confirmed else None
    last_l2 = l2_confirmed[-1] if l2_confirmed else None

    today = bars[-1].timestamp.date()
    latest_price = float(latest.close)

    print(f"\n  [{horizon}日预测] ─────────────────────────────")
    print(f"  分析日期: {today.strftime('%Y-%m-%d')}")
    print(f"  目标日期: {(today + timedelta(days=horizon)).strftime('%Y-%m-%d')} (T+{horizon})")

    # ---- 逐信号预测 ----
    for sig_label, last_sig in [("H2", last_h2), ("L2", last_l2)]:
        if last_sig is None:
            continue

        pred = re_engine.build_prediction(last_sig, final_state, latest_price)
        prob = float(pred.direction_prob)
        sig_date = last_sig.timestamp.date() if isinstance(last_sig.timestamp, datetime) else last_sig.timestamp
        sig_days_ago = (today - sig_date).days
        target_date = today + timedelta(days=horizon)

        # H2=看涨, L2=看跌
        if last_sig.setup_type.value == "H2":
            direction_str = "看涨 ▲" if prob > 0.5 else ("看跌 ▼" if prob < 0.5 else "中性")
        else:
            direction_str = "看跌 ▼" if prob > 0.5 else ("看涨 ▲" if prob < 0.5 else "中性")

        ev = cm.expected_value(
            prob, 1 - prob, 0.10,
            latest_price * 0.053, -latest_price * 0.025, latest_price,
        )
        k_pos = kelly_position(prob, float(pred.r_r_ratio))
        quality = float(last_sig.quality_score)

        print(f"\n  [{sig_label}] ────────────────────────────")
        print(f"  信号触发日:  {sig_date.strftime('%Y-%m-%d')}  (距今 {sig_days_ago} 天)")
        print(f"  信号质量:    {quality:.3f} ({'高' if quality >= 0.8 else '中' if quality >= 0.5 else '低'})")
        print(f"  预测时间线:  {sig_date.strftime('%Y-%m-%d')} ──[{sig_days_ago}d]──→ "
              f"{today.strftime('%Y-%m-%d')}(今天) ──[{horizon}d]──→ "
              f"{target_date.strftime('%Y-%m-%d')}(目标)")
        print(f"  方向概率:    {prob*100:.1f}% ({direction_str})")
        print(f"  目标达成率:  {float(pred.target_prob)*100:.1f}%  止损率: {float(pred.stop_prob)*100:.1f}%")
        print(f"  R:R = {float(pred.r_r_ratio):.2f}  期望收益: {ev*100:+.3f}% (含佣金+印花税+滑点)")
        print(f"  凯利仓位:    {k_pos*100:.2f}% (1/4 Kelly)")
        print(f"  置信度:      {pred.confidence_level}")

        # 存储用于汇总
        if sig_label == "H2":
            direction_prob = prob

    # ===== 4. 风控 =====
    rc = RiskConstraints()
    state = PortfolioState()
    ok, reason, pos = rc.evaluate(code, 0.08, state)
    va = VolatilityAnchor()
    if len(daily_ret) >= 20:
        scaled = va.scale_position(list(daily_ret[-20:]), list(daily_ret[-5:]), 0.08)
    else:
        scaled = 0.08

    risk_status = "ALL PASS" if ok else f"BLOCKED: {reason}"
    print(f"\n  [风控] 六层约束: {risk_status}")
    print(f"  波动率锚定仓位: {scaled*100:.2f}% (基础8%)")

    # ===== 5. 情绪分析 =====
    print(f"\n  [情绪采集] ─────────────────────────────")
    items = await sentiment.fetch(sector_id)
    if items:
        agg_score = sentiment.aggregate_sentiment(items)
        emoji = "🟢" if agg_score > 0.2 else ("🔴" if agg_score < -0.2 else "🟡")
        print(f"  聚合情绪: {agg_score:+.3f} {emoji}  (共{len(items)}条)")
        for item in items[:3]:
            src_map = {"official":"官方","media":"财经","research":"研报","social":"社交"}
            src_label = src_map.get(item["source"], item["source"])
            print(f"    [{src_label}] score={item['score']:+.2f}  {item['text'][:70]}")
    else:
        print(f"  无实时新闻数据 (最近24h无板块相关报道)")

    # ===== 6. 产业链 =====
    print(f"\n  [产业链] ─────────────────────────────")
    upstream = linkage.get_upstream_of(sector_id)
    downstream = linkage.get_downstream_of(sector_id)
    if upstream:
        print(f"  ↑ 上游: {', '.join(upstream)}")
    if downstream:
        print(f"  ↓ 下游: {', '.join(downstream)}")
    no_prefix_types = {"替代", "互补", "需求拉动"}
    for target, etype, strength in linkage.get_related_with_info(sector_id):
        if etype in no_prefix_types:
            print(f"  ↔ {target}: {etype}({strength})")

    # ===== 汇总 =====
    all_results[code] = {
        "name": name, "code": code, "sector_id": sector_id,
        "close": float(latest.close),
        "ret_5": ret_5, "ret_20": ret_20, "ret_60": ret_60,
        "vol_20": vol_20,
        "state": final_state.state.value if final_state else "neutral",
        "state_conf": float(final_state.confidence) if final_state else 0,
        "bull_pct": bull_pct,
        "confirmed": len(confirmed),
        "candidates": len(candidates),
        "prob": direction_prob,
        "direction": "看涨" if direction_prob > 0.5 else "看跌",
        "risk_ok": ok,
        "last_sig_date": confirmed[-1].timestamp.strftime("%Y-%m-%d") if confirmed else "N/A",
        "last_cand_date": candidates[-1].timestamp.strftime("%Y-%m-%d") if candidates else "N/A",
    }


async def main():
    for code, name, sector_id in ETF_LIST:
        await analyze_etf(code, name, sector_id)

    # ===== 对比总结 =====
    print()
    print()
    print("═" * 70)
    print("  三只ETF 对比总结")
    print("═" * 70)

    # 动态表头
    col_names = [name for _, name, _ in ETF_LIST]
    header = f"  {'指标':<20}"
    for cn in col_names:
        header += f" {cn:>16}"
    print(header)
    sep_width = 20 + 16 * len(ETF_LIST)
    print(f"  {'─'*sep_width}")

    metric_defs = [
        ("最新价",         "close",      "{:.4f}"),
        ("5日涨跌",        "ret_5",      "{:+.2f}%"),
        ("20日涨跌",       "ret_20",     "{:+.2f}%"),
        ("60日涨跌",       "ret_60",     "{:+.2f}%"),
        ("20日波动率",     "vol_20",     "{:.1f}%"),
        ("市场状态",       "state",      "{}"),
        ("BULL占比(120d)", "bull_pct",   "{:.0f}%"),
        ("确认态信号",     "confirmed",  "{}个"),
        ("候选态信号",     "candidates", "{}个"),
        ("方向概率",       "prob",       "{:.1%}"),
        ("方向判断",       "direction",  "{}"),
        ("最后信号日",     "last_sig_date", "{}"),
    ]

    for label, key, fmt in metric_defs:
        vals = []
        for code, _, _ in ETF_LIST:
            r = all_results[code]
            vals.append(fmt.format(r.get(key, "N/A")))
        row = f"  {label:<20}"
        for v in vals:
            row += f" {v:>16}"
        print(row)

    # 推荐排序
    print(f"\n  ── 综合推荐 ──")
    print()
    scored = []
    for code, name, _ in ETF_LIST:
        r = all_results[code]
        score = 0
        reasons = []

        if r["state"] == "bull":
            score += 3
            reasons.append("BULL趋势")
        elif r["state"] == "neutral":
            score += 1
            reasons.append("NEUTRAL")

        if r["confirmed"] >= 3:
            score += 3
            reasons.append(f"{r['confirmed']}个确认信号")
        elif r["confirmed"] >= 1:
            score += 2
            reasons.append(f"{r['confirmed']}个确认信号")
        else:
            reasons.append("无确认信号")

        if r["ret_5"] > 2:
            score += 2
            reasons.append("强短期动量")
        elif r["ret_5"] > 0:
            score += 1
            reasons.append("正短期动量")
        elif r["ret_5"] < -3:
            score -= 2
            reasons.append("弱短期动量")

        if r["ret_20"] > 5:
            score += 2
            reasons.append("强中期动量")
        elif r["ret_20"] > 0:
            score += 1
            reasons.append("正中期动量")

        if r["candidates"] >= 2:
            score += 1
            reasons.append(f"{r['candidates']}个候选态待确认")

        if not r["risk_ok"]:
            score -= 5
            reasons.append("风控警告!")

        if r["vol_20"] > 35:
            score -= 1
            reasons.append("高波动")

        if score >= 7:
            verdict = "★★★ 强烈关注"
        elif score >= 4:
            verdict = "★★ 重点关注"
        elif score >= 1:
            verdict = "★ 可观察"
        else:
            verdict = "暂观望"

        scored.append((score, name, verdict, reasons))

    scored.sort(reverse=True)
    for score, name, verdict, reasons in scored:
        print(f"  {name}: {verdict} (评分 {score})")
        print(f"    理由: {' / '.join(reasons)}")
        print()

    print("═" * 70)


if __name__ == "__main__":
    asyncio.run(main())
