"""SPAS 预测系统 — 用户输入指标 + 系统合成决策"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException

SPAS_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(SPAS_ROOT) not in sys.path:
    sys.path.insert(0, str(SPAS_ROOT))

from core.bridge.data_reader import (
    load_etf_data,
    list_available_etfs,
    get_etf_display_name,
)
from core.db.repository import (
    save_spas_history,
    get_spas_history,
    get_spas_history_entry,
    delete_spas_history,
)
from backend.schemas import (
    SPASAnalysisIn,
    SPASAnalysisOut,
    SPASProbabilityOut,
    SPASProbFactor,
    SPASHistoryItem,
    SPASHistoryDetail,
    SPASPositionOut,
    SPASRiskOut,
    SPASTechnicalOut,
)

router = APIRouter(prefix="/api/manual-analysis", tags=["手动指标分析"])


# ══════════════════════════════════════════════════════════════
# 核心分析引擎
# ══════════════════════════════════════════════════════════════

def _compute_ema(data: list[float], period: int) -> list[float]:
    """EMA 计算: α = 2/(N+1), EMA₁ = price₁"""
    result = []
    alpha = 2.0 / (period + 1.0)
    for i, price in enumerate(data):
        if i == 0:
            result.append(float(price))
        else:
            result.append(float(price) * alpha + result[-1] * (1 - alpha))
    return result


def _compute_kline_features(o: float, h: float, l: float, c: float) -> dict:
    """K线6维微观结构特征"""
    hl_range = h - l
    if hl_range <= 0:
        return {
            "body_ratio": 0.0,
            "close_position": 0.5,
            "upper_shadow": 0.0,
            "lower_shadow": 0.0,
        }
    return {
        "body_ratio": round(abs(c - o) / hl_range, 3),
        "close_position": round((c - l) / hl_range, 3),
        "upper_shadow": round((h - max(o, c)) / hl_range, 3),
        "lower_shadow": round((min(o, c) - l) / hl_range, 3),
    }


def _compute_technical(df: pd.DataFrame) -> SPASTechnicalOut:
    """从 OHLCV 自动计算 EMA、均线排列、K线特征"""
    close_data = list(df["close"].values)
    last = df.iloc[-1]

    current_price = float(last["close"])

    # EMA
    ema5 = _compute_ema(close_data, 5)
    ema10 = _compute_ema(close_data, 10)
    ema20 = _compute_ema(close_data, 20)
    ema60 = _compute_ema(close_data, 60) if len(close_data) >= 60 else [close_data[-1]]

    ema = {
        "ema5": round(ema5[-1], 3),
        "ema10": round(ema10[-1], 3),
        "ema20": round(ema20[-1], 3),
        "ema60": round(ema60[-1], 3),
    }

    # EMA 斜率 (近5日变化率)
    def slope(arr):
        if len(arr) >= 6:
            return round((arr[-1] - arr[-6]) / abs(arr[-6]) * 100, 3) if arr[-6] != 0 else 0.0
        return 0.0

    ema_slopes = {
        "ema5": slope(ema5),
        "ema10": slope(ema10),
        "ema20": slope(ema20),
    }

    # 均线排列
    if ema5[-1] > ema10[-1] > ema20[-1]:
        ma_alignment = "BULL"
    elif ema5[-1] < ema10[-1] < ema20[-1]:
        ma_alignment = "BEAR"
    else:
        ma_alignment = "NEUTRAL"

    # K线特征
    o, h, l, c = (
        float(last["open"]),
        float(last["high"]),
        float(last["low"]),
        float(last["close"]),
    )
    kline = _compute_kline_features(o, h, l, c)

    # K线形态判定
    if kline["close_position"] > 0.6 and kline["body_ratio"] > 0.3:
        kline_pattern = "bullish"
    elif kline["close_position"] < 0.4 and kline["body_ratio"] > 0.3:
        kline_pattern = "bearish"
    else:
        kline_pattern = "neutral"

    return SPASTechnicalOut(
        current_price=round(current_price, 2),
        ema=ema,
        ema_slopes=ema_slopes,
        ma_alignment=ma_alignment,
        kline_features=kline,
        kline_pattern=kline_pattern,
    )


def _synthesize_probability(
    inp: SPASAnalysisIn,
    tech: SPASTechnicalOut,
) -> SPASProbabilityOut:
    """合成涨跌概率 — 贝叶斯加权各因子贡献"""
    factors: list[SPASProbFactor] = []
    base = 0.50
    total_adjustment = 0.0

    # ──── 1. DMI 方向 ±10% ────
    if inp.adx > 25:
        if inp.plus_di > inp.minus_di:
            factors.append(SPASProbFactor(factor="DMI趋势", contribution=0.10, detail=f"ADX={inp.adx:.0f}, +DI>-DI"))
            total_adjustment += 0.10
        else:
            factors.append(SPASProbFactor(factor="DMI趋势", contribution=-0.10, detail=f"ADX={inp.adx:.0f}, -DI>+DI"))
            total_adjustment -= 0.10
    elif inp.adx > 18:
        if inp.plus_di > inp.minus_di:
            factors.append(SPASProbFactor(factor="DMI趋势", contribution=0.05, detail=f"ADX={inp.adx:.0f}(中等), +DI>-DI"))
            total_adjustment += 0.05
        else:
            factors.append(SPASProbFactor(factor="DMI趋势", contribution=-0.05, detail=f"ADX={inp.adx:.0f}(中等), -DI>+DI"))
            total_adjustment -= 0.05
    else:
        factors.append(SPASProbFactor(factor="DMI趋势", contribution=0.0, detail=f"ADX={inp.adx:.0f}<18, 无明确趋势"))

    # ──── 2. ASI 方向 ±6% ────
    asi_map = {"up": 0.06, "down": -0.06, "flat": 0.0}
    asi_contrib = asi_map.get(inp.asi_direction, 0.0)
    factors.append(SPASProbFactor(factor="ASI方向", contribution=asi_contrib, detail=f"ASI={inp.asi_value:.1f}, 方向={inp.asi_direction}"))
    total_adjustment += asi_contrib

    # ──── 3. MACD ±8% + 柱状态 ±3% ────
    if inp.dif > inp.dea:
        factors.append(SPASProbFactor(factor="MACD金叉区", contribution=0.08, detail=f"DIF={inp.dif:.3f}>DEA={inp.dea:.3f}"))
        total_adjustment += 0.08
    else:
        factors.append(SPASProbFactor(factor="MACD死叉区", contribution=-0.08, detail=f"DIF={inp.dif:.3f}<DEA={inp.dea:.3f}"))
        total_adjustment -= 0.08

    bar_map = {
        "red_increasing": (0.03, "红柱增长, 上涨动量增强"),
        "red_decreasing": (-0.03, "红柱缩短, 上涨动量减弱"),
        "green_increasing": (-0.03, "绿柱增长, 下跌动量增强"),
        "green_decreasing": (0.03, "绿柱缩短, 下跌动量减弱"),
    }
    bar_contrib, bar_detail = bar_map.get(inp.macd_bar, (0.0, "未知"))
    factors.append(SPASProbFactor(factor="MACD柱状态", contribution=bar_contrib, detail=bar_detail))
    total_adjustment += bar_contrib

    # ──── 4. RSI + WR 热度检查 ────
    # 同花顺 WR: 0=顶部(超买)  100=底部(超卖)
    # RSI<30 且 WR≥80 → 双重超卖 → +5%
    # RSI>70 且 WR≤20 → 双重超买 → -8%
    # RSI与WR背离 → -5%
    rsi_oversold = inp.rsi < 30
    rsi_overbought = inp.rsi > 70
    wr_oversold = inp.wr >= 80
    wr_overbought = inp.wr <= 20

    if rsi_oversold and wr_oversold:
        factors.append(SPASProbFactor(factor="RSI+WR双重超卖", contribution=0.05, detail=f"RSI={inp.rsi:.0f}, WR={inp.wr:.0f}"))
        total_adjustment += 0.05
    elif rsi_overbought and wr_overbought:
        factors.append(SPASProbFactor(factor="RSI+WR双重超买", contribution=-0.08, detail=f"RSI={inp.rsi:.0f}, WR={inp.wr:.0f}"))
        total_adjustment -= 0.08
    elif rsi_oversold and not wr_oversold:
        factors.append(SPASProbFactor(factor="RSI/WR背离", contribution=-0.05, detail=f"RSI={inp.rsi:.0f}超卖但WR={inp.wr:.0f}不确认"))
        total_adjustment -= 0.05
    elif rsi_overbought and not wr_overbought:
        factors.append(SPASProbFactor(factor="RSI/WR背离", contribution=-0.05, detail=f"RSI={inp.rsi:.0f}超买但WR={inp.wr:.0f}不确认"))
        total_adjustment -= 0.05
    else:
        note = "超卖反弹可能" if rsi_oversold else "超买回调风险" if rsi_overbought else "正常区间"
        factors.append(SPASProbFactor(factor="RSI热度", contribution=0.0, detail=f"RSI={inp.rsi:.0f}, {note}"))

    # ──── 5. OBV 方向 ±5% ────
    obv_map = {"up": 0.05, "down": -0.05, "flat": 0.0}
    obv_contrib = obv_map.get(inp.obv_direction, 0.0)
    factors.append(SPASProbFactor(factor="OBV方向", contribution=obv_contrib, detail=f"OBV={inp.obv_direction}"))
    total_adjustment += obv_contrib

    # ──── 6. OBV与价格背离检测 ────
    price_trend = tech.ma_alignment
    if inp.obv_direction == "down" and price_trend == "BULL":
        factors.append(SPASProbFactor(factor="OBV价格背离", contribution=-0.05, detail="价格上涨OBV下降, 量价背离"))
        total_adjustment -= 0.05
    if inp.obv_direction == "down" and tech.kline_pattern == "bullish":
        if not any(f.factor == "OBV价格背离" for f in factors):
            factors.append(SPASProbFactor(factor="OBV价格背离", contribution=-0.05, detail="K线看涨OBV下降, 量价背离"))
            total_adjustment -= 0.05

    # ──── 7. 量比缩放 ────
    if inp.volume_ratio > 1.5:
        factor_scale = 1.3  # 放量确认 → 方向信号放大30%
    elif inp.volume_ratio > 1.2:
        factor_scale = 1.15
    elif inp.volume_ratio < 0.5:
        factor_scale = 0.6  # 极度缩量 → 信号打折40%
    elif inp.volume_ratio < 0.7:
        factor_scale = 0.8
    else:
        factor_scale = 1.0

    factors.append(SPASProbFactor(
        factor="量比缩放",
        contribution=0.0,
        detail=f"量比={inp.volume_ratio:.2f}, 缩放系数={factor_scale:.2f} (应用于方向信号)",
    ))

    # ──── 8. 大盘环境衰减 ────
    market_decay = {"bull": 1.0, "range": 0.6, "bear": 0.3}
    decay = market_decay.get(inp.market_trend, 0.6)
    if inp.market_adx > 25 and inp.market_trend == "bear":
        decay = 0.2  # 大盘强熊 → 更大力衰减
    factors.append(SPASProbFactor(
        factor="大盘环境",
        contribution=0.0,
        detail=f"大盘={inp.market_trend}, ADX={inp.market_adx:.0f}, 衰减系数={decay:.2f}",
    ))

    # ──── 9. 均线排列 ±5% ────
    ma_contrib = {"BULL": 0.05, "BEAR": -0.05, "NEUTRAL": 0.0}
    ma_c = ma_contrib.get(tech.ma_alignment, 0.0)
    factors.append(SPASProbFactor(factor="均线排列", contribution=ma_c, detail=f"均线={tech.ma_alignment}"))
    total_adjustment += ma_c

    # ──── 10. K线形态 ±3% ────
    kline_contrib = {"bullish": 0.03, "bearish": -0.03, "neutral": 0.0}
    kl_c = kline_contrib.get(tech.kline_pattern, 0.0)
    factors.append(SPASProbFactor(factor="K线形态", contribution=kl_c, detail=f"收盘位置={tech.kline_features['close_position']:.2f}, 实体比={tech.kline_features['body_ratio']:.2f}"))
    total_adjustment += kl_c

    # ──── 应用量比缩放和盘衰减到方向信号 ────
    # 方向信号 = DMI + ASI + MACD + OBV + 均线 + K线(不含热度/背离因子)
    # 简化为：对 net 方向调整应用缩放
    net_directional_parts = [
        asi_contrib, bar_contrib, obv_contrib, ma_c, kl_c,
    ]
    # DMI 和 MACD 的贡献
    for f in factors:
        if f.factor in ("DMI趋势", "MACD金叉区", "MACD死叉区"):
            net_directional_parts.append(f.contribution)

    # 非方向性部分 = 热度 + 背离
    non_dir_parts = []
    for f in factors:
        if f.factor in ("RSI+WR双重超卖", "RSI+WR双重超买", "RSI/WR背离", "OBV价格背离"):
            non_dir_parts.append(f.contribution)

    net_dir = sum(net_directional_parts)
    net_non_dir = sum(non_dir_parts)

    # 方向部分 * 量比缩放 * 大盘衰减
    adjusted_dir = net_dir * factor_scale * decay

    # 最终合成
    final = base + adjusted_dir + net_non_dir

    # Clamp
    final = max(0.25, min(0.85, final))

    # 方向判定
    if final >= 0.55:
        direction = "bullish"
    elif final <= 0.45:
        direction = "bearish"
    else:
        direction = "neutral"

    return SPASProbabilityOut(
        direction=direction,
        probability=round(final, 3),
        base_probability=base,
        factors=factors,
    )


def _compute_position(
    prob: float,
    rr_ratio: float,
    psychology_answers: list[int],
) -> SPASPositionOut:
    """Kelly 仓位 + 心理问卷调整"""
    # Kelly: f* = (p*b - q) / b
    p = prob
    b = rr_ratio
    q = 1.0 - p
    kelly = (p * b - q) / b if b > 0 else 0.0

    # 心理评分
    total_score = sum(psychology_answers)
    psych_factor = 0.50 + (total_score / 30.0) * 0.50  # [0.5, 1.0]

    # 心理等级
    if total_score >= 25:
        psych_level = "优秀"
    elif total_score >= 20:
        psych_level = "良好"
    elif total_score >= 15:
        psych_level = "一般"
    else:
        psych_level = "需改善"

    # 心理警告
    warnings = []
    low_items = [i + 1 for i, a in enumerate(psychology_answers) if a <= 1]
    if len(low_items) >= 3:
        warnings.append(f"第{','.join(map(str, low_items))}题得分偏低，建议审视交易心态")
    if psychology_answers[-1] <= 1:
        warnings.append("当前仓位较重，新仓位建议更保守")

    # 仓位三段式判定
    if p >= 0.55:
        # 看多：正常 Kelly
        kelly_frac = max(0.0, kelly / 4.0)
        suggested = round(kelly_frac * psych_factor * 100, 1)
    elif p >= 0.45:
        # 方向不明：半仓 Kelly
        kelly_frac = max(0.0, kelly / 8.0)
        suggested = round(kelly_frac * psych_factor * 100, 1)
        warnings.append("方向不明确(概率45%~55%)，建议减半仓位或观望")
    else:
        # 看空：不建议买入
        kelly_frac = 0.0
        suggested = 0.0
        warnings.append("当前方向偏空(概率<45%)，不建议买入")

    if kelly <= 0:
        warnings.append("Kelly公式f*≤0, 建议不交易")

    return SPASPositionOut(
        kelly_f_star=round(kelly, 4),
        kelly_fractional=round(kelly_frac, 4),
        psychology_score=total_score,
        psychology_factor=round(psych_factor, 3),
        psychology_level=psych_level,
        psychology_warnings=warnings,
        suggested_position_pct=max(0.0, suggested),
    )


def _compute_risk(
    current_price: float,
    atr: float,
    rr_ratio: float,
    max_loss_pct: float,
) -> SPASRiskOut:
    """止损/止盈计算"""
    # ATR 合理性检测：不应超过当前价的 20%
    atr_warn = atr > current_price * 0.2

    atr_stop = 2.0 * atr
    stop_price = current_price - atr_stop
    stop_pct = round((stop_price - current_price) / current_price * 100, 2)

    take_profit_price = current_price + rr_ratio * atr_stop
    take_profit_pct = round((take_profit_price - current_price) / current_price * 100, 2)

    # 止损不超过最大亏损限制
    capped = False
    max_loss_price = current_price * (1.0 - max_loss_pct / 100.0)
    if stop_price < max_loss_price:
        stop_price = max_loss_price
        stop_pct = -max_loss_pct
        capped = True

    # 止盈安全上限：不超过当前价 3 倍
    tp_max = current_price * 3.0
    tp_capped = False
    if take_profit_price > tp_max:
        take_profit_price = tp_max
        take_profit_pct = round((take_profit_price - current_price) / current_price * 100, 2)
        tp_capped = True

    return SPASRiskOut(
        current_price=round(current_price, 2),
        atr=round(atr, 4),
        atr_multiplier=2,
        stop_loss_price=round(stop_price, 2),
        stop_loss_pct=round(stop_pct, 2),
        take_profit_price=round(take_profit_price, 2),
        take_profit_pct=round(take_profit_pct, 2),
        rr_ratio=rr_ratio,
        stop_capped_by_max_loss=capped,
        tp_capped=tp_capped,
        atr_warning=atr_warn,
    )


# ══════════════════════════════════════════════════════════════
# API 端点
# ══════════════════════════════════════════════════════════════

@router.post("/analysis/{code}", response_model=SPASAnalysisOut)
def analyze(code: str, inp: SPASAnalysisIn):
    """核心分析端点：用户输入指标值 → 系统合成决策"""
    # 1. 加载 OHLCV 数据
    df = load_etf_data(code, "day")
    if df is None or len(df) < 10:
        raise HTTPException(status_code=404, detail=f"ETF 数据不足或不存在: {code}")

    # 2. 自动计算技术指标
    tech = _compute_technical(df)

    # 2.5 用户实时价格覆盖
    if inp.current_price is not None and inp.current_price > 0:
        tech.current_price = inp.current_price

    # 3. 合成涨跌概率
    probability = _synthesize_probability(inp, tech)

    # 4. 计算仓位
    position = _compute_position(probability.probability, inp.rr_ratio, inp.psychology_answers)

    # 5. 计算止盈止损
    risk = _compute_risk(tech.current_price, inp.atr, inp.rr_ratio, inp.max_loss_pct)

    result = SPASAnalysisOut(
        symbol=code,
        display_name=get_etf_display_name(code),
        timestamp=str(df.iloc[-1]["trade_date"])[:10],
        probability=probability,
        position=position,
        risk=risk,
        technical=tech,
    )

    # 6. 自动保存历史
    try:
        save_spas_history(
            etf_code=code,
            etf_name=get_etf_display_name(code),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            probability=probability.probability,
            direction=probability.direction,
            position_pct=position.suggested_position_pct,
            stop_loss=risk.stop_loss_price,
            take_profit=risk.take_profit_price,
            psychology_score=position.psychology_score,
            psychology_level=position.psychology_level,
            inputs_json=inp.model_dump_json(),
            result_json=result.model_dump_json(),
        )
    except Exception:
        pass  # 保存失败不影响分析结果

    return result


# ── History ────────────────────────────────────────────

@router.get("/history", response_model=list[SPASHistoryItem])
def list_history(limit: int = 20):
    """获取历史分析记录"""
    rows = get_spas_history(limit)
    return [
        SPASHistoryItem(
            id=r["id"], etf_code=r["etf_code"], etf_name=r["etf_name"],
            created_at=r["created_at"], probability=r["probability"],
            direction=r["direction"], position_pct=r["position_pct"],
            stop_loss=r["stop_loss"], take_profit=r["take_profit"],
            psychology_score=r["psychology_score"], psychology_level=r["psychology_level"],
        )
        for r in rows
    ]


@router.get("/history/{entry_id}", response_model=SPASHistoryDetail)
def get_history(entry_id: int):
    """获取单条历史记录详情"""
    r = get_spas_history_entry(entry_id)
    if not r:
        raise HTTPException(status_code=404, detail="记录不存在")
    return SPASHistoryDetail(
        id=r["id"], etf_code=r["etf_code"], etf_name=r["etf_name"],
        created_at=r["created_at"], probability=r["probability"],
        direction=r["direction"], position_pct=r["position_pct"],
        stop_loss=r["stop_loss"], take_profit=r["take_profit"],
        psychology_score=r["psychology_score"], psychology_level=r["psychology_level"],
        inputs=json.loads(r["inputs_json"]) if isinstance(r["inputs_json"], str) else r["inputs_json"],
        result=json.loads(r["result_json"]) if isinstance(r["result_json"], str) else r["result_json"],
    )


@router.delete("/history/{entry_id}")
def delete_history(entry_id: int):
    """删除历史记录"""
    ok = delete_spas_history(entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"ok": True}


@router.get("/system-info")
def system_info():
    """系统状态：数据新鲜度、ETF 覆盖"""
    etfs = list_available_etfs()
    data_dir = SPAS_ROOT / "data"
    latest_mtime = 0
    for f in data_dir.glob("*_day.parquet"):
        mtime = os.path.getmtime(f)
        if mtime > latest_mtime:
            latest_mtime = mtime
    update_time = datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M") if latest_mtime else "未知"

    latest_date = "未知"
    if etfs:
        max_date = ""
        for e in etfs[:20]:
            try:
                df2 = load_etf_data(e["code"], "day")
                if df2 is not None and len(df2) > 0:
                    d = str(df2.iloc[-1]["trade_date"])[:10]
                    if d > max_date:
                        max_date = d
            except Exception:
                pass
        if max_date:
            latest_date = max_date

    return {
        "etf_count": len(etfs),
        "data_updated": update_time,
        "data_latest_date": latest_date,
        "data_dir": str(data_dir),
    }


@router.post("/update-data")
def trigger_data_update():
    """使用 akshare 更新全部 ETF 日线数据"""
    etfs = list_available_etfs()
    if not etfs:
        return {"success": False, "message": "没有可用的 ETF"}

    try:
        import akshare as ak
    except ImportError:
        raise HTTPException(status_code=500, detail="akshare 未安装")

    results = []
    data_dir = SPAS_ROOT / "data"

    for e in etfs:
        code = e["code"]
        symbol = code.replace(".SH", "").replace(".SZ", "")

        df = None
        last_error = ""
        for attempt in range(3):
            try:
                df = ak.fund_etf_hist_em(
                    symbol=symbol, period="daily",
                    start_date="20200101", end_date="20991231", adjust="qfq",
                )
                break
            except Exception as ex:
                last_error = str(ex)[:80]
                time.sleep(1.5)

        if df is None or (hasattr(df, "empty") and df.empty):
            results.append({"code": code, "status": "empty", "error": last_error})
            time.sleep(0.5)
            continue

        try:
            col_map = {"日期": "trade_date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"}
            df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
            df["trade_date"] = df["trade_date"].astype(str)
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            out_cols = [c for c in ["trade_date", "open", "high", "low", "close", "volume"] if c in df.columns]
            df[out_cols].to_parquet(data_dir / f"{code}_day.parquet", index=False)
            last_date = str(df["trade_date"].iloc[-1])[:10] if "trade_date" in df.columns else "?"
            results.append({"code": code, "status": "ok", "bars": len(df), "last_date": last_date})
        except Exception as ex:
            results.append({"code": code, "status": "error", "error": str(ex)[:100]})

        time.sleep(1.2)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    return {"success": ok_count > 0, "total": len(etfs), "updated": ok_count, "results": results}
