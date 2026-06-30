"""投资学院 — Streamlit 主入口"""
import sys
from pathlib import Path

# 确保 investment_academy 在 sys.path 中
ACADEMY_ROOT = Path(__file__).resolve().parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

import streamlit as st

st.set_page_config(
    page_title="投资学院",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 自定义 CSS ──────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .phase-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    .phase-card h3 {
        color: white;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# ── 侧边栏导航 ─────────────────────────────────────
st.sidebar.title("📈 投资学院")

menu = st.sidebar.radio(
    "导航",
    [
        "🏠 首页",
        "📚 知识轨道",
        "🔬 实践轨道",
        "🎮 交易沙盒",
        "📊 学习进度",
    ],
    label_visibility="collapsed",
)

# ── 页面路由 ───────────────────────────────────────
if menu == "🏠 首页":
    st.markdown('<p class="main-header">📈 投资学院</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">从零基础到投资大拿 — 系统化掌握股市与投资知识</p>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="phase-card">
            <h3>📚 知识轨道</h3>
            <p>7个阶段 · 34章系统学习</p>
            <p>从股市基础概念到完整交易系统，循序渐进</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="phase-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>🔬 实践轨道</h3>
            <p>6个实验室 · 动手探索</p>
            <p>用真实市场数据做实验，理解每个概念的实际含义</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="phase-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>🎮 交易沙盒</h3>
            <p>零风险模拟交易</p>
            <p>用历史数据练习交易决策，积累实战经验</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🚀 快速开始")
    st.markdown("""
    1. **如果你是纯新手** → 从 📚 知识轨道 → P1 股市基础开始
    2. **如果你想动手实践** → 去 🔬 实践轨道 → M1 数据勘探实验室
    3. **如果你想测试自己** → 用 🎮 交易沙盒模拟真实交易
    """)

    st.subheader("🗺️ 学习路径")

    import pandas as pd
    path_data = [
        {"阶段": "P1 股市基础", "主题": "股票/ETF/K线/交易规则", "章节": "5章", "建议时间": "2天"},
        {"阶段": "P2 技术分析", "主题": "趋势/微观结构/均线/Wyckoff", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P3 板块产业链", "主题": "行业分类/产业链/板块轮动", "章节": "4章", "建议时间": "2天"},
        {"阶段": "P4 量化策略", "主题": "概率思维/规则策略/ML融合", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P5 风险管理", "主题": "仓位/回撤/波动率/尾部风险", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P6 交易心理", "主题": "情绪管理/认知偏差/市场情绪", "章节": "6章", "建议时间": "3天"},
        {"阶段": "P7 实战整合", "主题": "回测/偏差/完整交易系统", "章节": "4章", "建议时间": "2天"},
    ]
    st.dataframe(pd.DataFrame(path_data), use_container_width=True, hide_index=True)

elif menu == "📚 知识轨道":
    from interactive.content_loader import list_phases

    phases = list_phases()
    phase_names = {
        "p1_basics": "P1: 股市基础",
        "p2_technical": "P2: 技术分析入门",
        "p3_sectors": "P3: 板块与产业链",
        "p4_quant": "P4: 量化策略思维",
        "p5_risk": "P5: 风险管理",
        "p6_psychology": "P6: 交易心理与市场情绪",
        "p7_integration": "P7: 实战整合",
    }

    phase_options = []
    for p in phases:
        name = phase_names.get(p["id"], p["id"])
        phase_options.append(f"{name} ({p['chapter_count']}章)")

    if phase_options:
        selected = st.sidebar.selectbox("选择阶段", phase_options)
        selected_id = phases[phase_options.index(selected)]["id"]

        module_name = f"pages.knowledge.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"📝 {phase_names.get(selected_id, selected_id)} 内容正在编写中…")
        except ImportError as e:
            st.info(f"📝 {phase_names.get(selected_id, selected_id)} 内容正在编写中…")
    else:
        st.info("暂无可用章节内容")

elif menu == "🔬 实践轨道":
    from interactive.content_loader import list_labs

    labs = list_labs()
    lab_names = {
        "m1_data_lab": "M1: 数据勘探实验室",
        "m2_feature_lab": "M2: 特征工程实验室",
        "m3_prediction": "M3: 预测引擎探索",
        "m4_risk_sandbox": "M4: 风控沙盒",
        "m5_backtest": "M5: 回测分析器",
        "m6_sentiment": "M6: 市场情绪实验室",
    }

    lab_options = [lab_names.get(l["id"], l["id"]) for l in labs]
    if lab_options:
        selected = st.sidebar.selectbox("选择实验室", lab_options)
        selected_id = labs[lab_options.index(selected)]["id"]

        module_name = f"pages.practice.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"🔬 {lab_names.get(selected_id, selected_id)} 正在建设中…")
        except ImportError as e:
            st.info(f"🔬 {lab_names.get(selected_id, selected_id)} 正在建设中…")
    else:
        st.info("暂无可用实验")

elif menu == "🎮 交易沙盒":
    st.markdown("## 🎮 交易沙盒")
    st.info("🚧 交易沙盒正在建设中… 完成后你将可以在这里用历史数据模拟真实交易决策。")

elif menu == "📊 学习进度":
    st.markdown("## 📊 学习进度")
    st.info("🚧 学习进度仪表盘正在建设中…")
