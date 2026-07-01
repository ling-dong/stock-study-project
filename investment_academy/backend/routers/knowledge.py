"""知识提取器 API — Bridge 层投资知识暴露"""
from fastapi import APIRouter
from bridge.knowledge_extractor import (
    extract_sector_list,
    extract_factor_definitions,
    extract_market_state_params,
    extract_risk_constraints,
    extract_setup_definitions,
)

router = APIRouter(prefix="/api/knowledge", tags=["投资知识"])


@router.get("/sectors")
def get_sectors():
    """14 个行业列表 + ETF 代码"""
    return extract_sector_list()


@router.get("/factors")
def get_factors():
    """6 维 K 线微观结构特征因子定义"""
    return extract_factor_definitions()


@router.get("/market-params")
def get_market_params():
    """市场状态机参数 (EMA/ADX/置信度等)"""
    return extract_market_state_params()


@router.get("/risk-constraints")
def get_risk_constraints():
    """4 层风控约束"""
    return extract_risk_constraints()


@router.get("/setups")
def get_setups():
    """3 种 Wyckoff Setup 模式定义 (H2/L2/FB)"""
    return extract_setup_definitions()
