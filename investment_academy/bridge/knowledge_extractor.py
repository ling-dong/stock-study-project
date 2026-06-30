"""SPAS 知识提取器 — 从配置和代码中提取投资知识（纯函数，SPAS 不可用时回退）"""
from pathlib import Path
from typing import Optional

import yaml

SPAS_ROOT = Path(__file__).resolve().parent.parent.parent


def extract_sector_list() -> list[dict]:
    """从 config/sectors.yaml 提取行业列表及 ETF 信息"""
    sectors_path = SPAS_ROOT / "config" / "sectors.yaml"
    if not sectors_path.exists():
        return _fallback_sectors()

    with open(sectors_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    sectors = []
    raw_list = data.get("sectors", [])
    if isinstance(raw_list, list):
        for entry in raw_list:
            if isinstance(entry, dict):
                sector_id = entry.get("sector_id", "")
                constituents_raw = entry.get("constituents", [])
                constituents = [c.get("code", "") for c in constituents_raw if isinstance(c, dict)][:3]
                sectors.append({
                    "id": sector_id,
                    "name": entry.get("name", sector_id),
                    "etf_code": entry.get("etf_code", ""),
                    "constituents": constituents,
                    "related_sectors": entry.get("related_sectors", []),
                })
    return sectors


def extract_factor_definitions() -> list[dict]:
    """提取 K 线特征因子定义（6维）"""
    return [
        {
            "name": "body_ratio",
            "chinese": "实体比",
            "formula": "|Close - Open| / (High - Low)",
            "meaning": "烛体占整体振幅的比例，反映多空博弈强度",
            "range": "[0, 1]",
        },
        {
            "name": "close_position",
            "chinese": "收盘位置",
            "formula": "(Close - Low) / (High - Low)",
            "meaning": "收盘价在整体区间的位置。>0.5 买方强势，<0.5 卖方强势",
            "range": "[0, 1]",
        },
        {
            "name": "upper_shadow",
            "chinese": "上影线比例",
            "formula": "(High - max(Open, Close)) / (High - Low)",
            "meaning": "上方抛压强度。值越大上方阻力越大",
            "range": "[0, 1]",
        },
        {
            "name": "lower_shadow",
            "chinese": "下影线比例",
            "formula": "(min(Open, Close) - Low) / (High - Low)",
            "meaning": "下方支撑强度。值越大下方支撑越强",
            "range": "[0, 1]",
        },
        {
            "name": "trend_bar",
            "chinese": "趋势棒方向",
            "formula": "Close > Open → +1 (阳线), Close < Open → -1 (阴线), Close ≈ Open → 0 (十字星)",
            "meaning": "单根K线的涨跌方向",
            "range": "{-1, 0, +1}",
        },
        {
            "name": "limit_status",
            "chinese": "涨跌停状态（A股特有）",
            "formula": "价格触及涨跌停板 → ±1，正常 → 0",
            "meaning": "检测是否触及A股特有的±10%涨跌停限制",
            "range": "{-1, 0, +1}",
        },
    ]


def extract_market_state_params() -> dict:
    """提取市场状态机参数"""
    settings_path = SPAS_ROOT / "config" / "settings.yaml"
    if not settings_path.exists():
        return _fallback_market_params()

    with open(settings_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    market = data.get("market_state", {})
    return {
        "ema_period": market.get("ema_period", 20),
        "bull_trend_bar_ratio": market.get("trend_bar_ratio_bull", 0.40),
        "adx_threshold": market.get("adx_threshold", 18),
        "confirmation_bars": market.get("confirmation_bars", 2),
        "confidence_initial": market.get("initial_confidence", 0.3),
        "confidence_increment": market.get("confidence_per_bar", 0.05),
        "confidence_max": market.get("max_confidence", 0.9),
    }


def extract_risk_constraints() -> list[dict]:
    """提取风控约束层级"""
    settings_path = SPAS_ROOT / "config" / "settings.yaml"
    if not settings_path.exists():
        return _fallback_risk_constraints()

    with open(settings_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    constraints = data.get("risk_constraints", {})
    if isinstance(constraints, dict):
        layer_map = {
            "L1_daily_stop": ("L1", "日亏损 -{:.0%}", "禁止新开仓"),
            "L2_weekly_stop": ("L2", "周亏损 -{:.0%}", "减仓50%"),
            "L3_monthly_stop": ("L3", "月度亏损 -{:.0%}", "强制清仓"),
            "L4_max_drawdown": ("L4", "最大回撤 -{:.0%}", "强制清仓"),
        }
        result = []
        for key, value in constraints.items():
            if key in layer_map and isinstance(value, (int, float)):
                layer, threshold_tpl, action = layer_map[key]
                threshold = threshold_tpl.format(abs(value))
                result.append({"layer": layer, "threshold": threshold, "action": action})
        if result:
            return result
    return _fallback_risk_constraints()


def extract_setup_definitions() -> list[dict]:
    """提取 Setup 模式定义"""
    return [
        {
            "name": "H2",
            "chinese": "双底回调",
            "theory": "Wyckoff",
            "description": "上升趋势中的两段式回调，每次回调低点抬高。牛市延续信号。",
            "base_winrate": 0.55,
            "quality_factors": ["回调幅度相近(35%)", "成交量收缩(30%)", "突破力度(35%)"],
        },
        {
            "name": "L2",
            "chinese": "双顶反弹",
            "theory": "Wyckoff",
            "description": "下降趋势中的两段式反弹，每次反弹高点降低。熊市延续信号。",
            "base_winrate": 0.55,
            "quality_factors": ["反弹幅度相近(35%)", "成交量收缩(30%)", "突破力度(35%)"],
        },
        {
            "name": "FB",
            "chinese": "假突破",
            "theory": "Wyckoff",
            "description": "价格突破关键位后迅速反转，形成陷阱。趋势衰竭信号。",
            "base_winrate": 0.45,
            "quality_factors": ["突破强弱(30%)", "反转速度(40%)", "成交量确认(30%)"],
        },
    ]


# ── 回退数据 ──

def _fallback_sectors() -> list[dict]:
    return [
        {"id": "801010", "name": "农林牧渔", "etf_code": "159825.SZ"},
        {"id": "801120", "name": "食品饮料", "etf_code": "515170.SH"},
        {"id": "801180", "name": "医药生物", "etf_code": "512010.SH"},
    ]


def _fallback_market_params() -> dict:
    return {
        "ema_period": 20,
        "bull_trend_bar_ratio": 0.40,
        "adx_threshold": 18,
        "confirmation_bars": 2,
    }


def _fallback_risk_constraints() -> list[dict]:
    return [
        {"layer": "L4", "threshold": "最大回撤 -20%", "action": "强制清仓"},
        {"layer": "L3", "threshold": "月度亏损 -15%", "action": "强制清仓"},
        {"layer": "L2", "threshold": "周亏损 -8%", "action": "减仓50%"},
        {"layer": "L1", "threshold": "日亏损 -3%", "action": "禁止新开仓"},
    ]
