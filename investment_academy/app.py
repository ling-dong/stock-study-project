"""投资学院 — Streamlit 主入口（暗色专业版）"""
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

# ══════════════════════════════════════════════════════════════
# ── 全局 CSS ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ── 整体基调 ── */
    .stApp {
        background: #0B0E11;
    }
    .main > div {
        background: #0B0E11;
        padding: 0 1rem 2rem;
    }
    /* 隐藏 Streamlit 默认装饰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    /* ── 滚动条 ── */
    ::-webkit-scrollbar {width: 6px; height: 6px;}
    ::-webkit-scrollbar-track {background: #0B0E11;}
    ::-webkit-scrollbar-thumb {background: #F0B90B44; border-radius: 3px;}
    ::-webkit-scrollbar-thumb:hover {background: #F0B90B88;}

    /* ── 排版 ── */
    h1, h2, h3, h4, h5, h6 {
        color: #EAECEF !important;
        letter-spacing: 0.02em;
    }
    h1 {font-size: 2.4rem !important; font-weight: 800 !important; margin-bottom: 0.25rem !important;}
    h2 {font-size: 1.6rem !important; font-weight: 700 !important; margin-top: 1.5rem !important; border-bottom: 1px solid #F0B90B22; padding-bottom: 0.4rem;}
    h3 {font-size: 1.15rem !important; font-weight: 600 !important;}
    p, li, div, span {color: #EAECEF;}

    /* ── Hero 区 ── */
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #F0B90B 0%, #F5D76E 50%, #F0B90B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #848E9C;
        margin-bottom: 1.8rem;
    }

    /* ── Metric 卡片 ── */
    .metric-card {
        background: linear-gradient(145deg, #1E2329, #15191E);
        border: 1px solid #2B3139;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    .metric-card:hover {
        border-color: #F0B90B55;
        box-shadow: 0 4px 30px rgba(240,185,11,0.08);
    }
    .metric-card .icon {font-size: 1.8rem; line-height: 1;}
    .metric-card .num {
        font-size: 2rem;
        font-weight: 800;
        color: #F0B90B;
        margin: 0.3rem 0 0.1rem;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #848E9C;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .metric-card .delta {
        font-size: 0.75rem;
        color: #0ECB81;
        margin-top: 0.1rem;
    }

    /* ── 继续学习按钮 ── */
    div.continue-btn-wrap {
        display: flex;
        justify-content: center;
        margin: 1.2rem 0 2rem;
    }
    .continue-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: linear-gradient(135deg, #F0B90B 0%, #D4A409 100%);
        color: #0B0E11 !important;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.65rem 2.2rem;
        border-radius: 40px;
        text-decoration: none;
        box-shadow: 0 0 20px rgba(240,185,11,0.25);
        transition: all 0.3s;
        cursor: pointer;
        border: none;
    }
    .continue-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 35px rgba(240,185,11,0.45);
    }

    /* ── 特性卡片 ── */
    .feature-grid {display: flex; gap: 1.2rem; flex-wrap: wrap;}
    .feature-card {
        flex: 1;
        min-width: 200px;
        background: #1E2329;
        border: 1px solid #2B3139;
        border-radius: 14px;
        padding: 1.5rem;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #F0B90B, #F5D76E);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .feature-card:hover::before {opacity: 1;}
    .feature-card:hover {
        border-color: #F0B90B44;
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    .feature-card .fc-icon {font-size: 2.2rem;}
    .feature-card .fc-title {font-size: 1.1rem; font-weight: 700; color: #EAECEF; margin: 0.5rem 0 0.3rem;}
    .feature-card .fc-desc {font-size: 0.85rem; color: #848E9C; line-height: 1.5;}
    .feature-card .fc-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-top: 0.6rem;
        background: #F0B90B22;
        color: #F0B90B;
        border: 1px solid #F0B90B44;
    }

    /* ── 时间线 ── */
    .timeline {position: relative; padding-left: 2rem; margin: 1.5rem 0 0.5rem;}
    .timeline::before {
        content: "";
        position: absolute;
        left: 6px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #F0B90B, #F0B90B44, transparent);
    }
    .tl-item {
        position: relative;
        padding: 0.55rem 0 0.55rem 1.2rem;
        border-left: 2px solid transparent;
    }
    .tl-item:not(:last-child) {margin-bottom: 0.2rem;}
    .tl-dot {
        position: absolute;
        left: -1.85rem;
        top: 0.65rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #F0B90B;
        border: 2px solid #0B0E11;
        box-shadow: 0 0 0 2px #F0B90B66;
    }
    .tl-dot.completed {background: #0ECB81; box-shadow: 0 0 0 2px #0ECB8166;}
    .tl-dot.active {background: #F0B90B; box-shadow: 0 0 0 4px #F0B90B44; animation: pulse-dot 2s infinite;}
    .tl-phase {font-weight: 700; color: #EAECEF; font-size: 0.95rem;}
    .tl-phase.completed {color: #0ECB81;}
    .tl-topic {font-size: 0.78rem; color: #848E9C;}
    .tl-meta {font-size: 0.72rem; color: #5E6673; margin-left: 0.6rem;}
    @keyframes pulse-dot {
        0%, 100% {box-shadow: 0 0 0 4px #F0B90B44;}
        50% {box-shadow: 0 0 0 8px #F0B90B22;}
    }

    /* ── 阶段/实验室卡片（知识/实践轨道） ── */
    .track-card {
        background: #1E2329;
        border: 1px solid #2B3139;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.9rem;
        cursor: pointer;
        transition: all 0.25s;
        position: relative;
    }
    .track-card:hover {
        border-color: #F0B90B66;
        box-shadow: 0 6px 25px rgba(240,185,11,0.08);
        transform: translateX(4px);
    }
    .track-card.selected {
        border-color: #F0B90B;
        box-shadow: 0 0 0 1px #F0B90B, 0 6px 25px rgba(240,185,11,0.12);
    }
    .track-card .tc-header {
        display: flex; justify-content: space-between; align-items: center;
    }
    .track-card .tc-name {font-size: 1.05rem; font-weight: 700; color: #EAECEF;}
    .track-card .tc-count {font-size: 0.78rem; color: #848E9C;}
    .track-card .tc-bar-wrap {
        margin-top: 0.5rem;
        height: 4px;
        background: #2B3139;
        border-radius: 2px;
        overflow: hidden;
    }
    .track-card .tc-bar-fill {
        height: 100%;
        border-radius: 2px;
        background: linear-gradient(90deg, #F0B90B, #F5D76E);
        transition: width 0.6s ease;
    }
    .tc-badge {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        border: 1px solid;
    }
    .tc-badge.not-started {background: #2B3139; color: #848E9C; border-color: #2B3139;}
    .tc-badge.in-progress {background: #F0B90B22; color: #F0B90B; border-color: #F0B90B44; animation: pulse-badge 2s infinite;}
    .tc-badge.completed {background: #0ECB8122; color: #0ECB81; border-color: #0ECB8144;}
    @keyframes pulse-badge {
        0%, 100% {opacity: 1;}
        50% {opacity: 0.6;}
    }

    /* ── 章节列表 ── */
    .ch-list {margin: 1rem 0 0.5rem;}
    .ch-item {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .ch-item:hover {background: #1E2329;}
    .ch-item .ch-icon {font-size: 1.1rem; width: 1.5rem; text-align: center;}
    .ch-item .ch-icon.done {color: #0ECB81;}
    .ch-item .ch-icon.pending {color: #5E6673;}
    .ch-item .ch-title {font-size: 0.9rem; color: #EAECEF; flex: 1;}

    /* sidebar 样式由 config.toml 的 secondaryBackgroundColor 控制 */

    /* ── 横向分割线 ── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #F0B90B33, transparent);
        margin: 1.5rem 0;
    }
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #F0B90B22, transparent);
        margin: 1.5rem 0;
    }

    /* ── 按钮主题覆盖 ── */
    .stButton > button {
        background: #F0B90B !important;
        color: #0B0E11 !important;
        font-weight: 700 !important;
        border-radius: 40px !important;
        border: none !important;
        padding: 0.4rem 1.8rem !important;
        transition: all 0.25s !important;
        box-shadow: 0 0 12px rgba(240,185,11,0.15) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 0 25px rgba(240,185,11,0.3) !important;
    }

    /* ── 信息 / 成功 / 警告 / 错误框 ── */
    div[data-testid="stAlert"] {
        background: #1E2329 !important;
        border: 1px solid #2B3139 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] > div:first-child {
        background: transparent !important;
        border: none !important;
    }

    /* ── Selectbox / radio / text input 暗色适配 ── */
    div[data-baseweb="select"] > div {
        background-color: #1E2329 !important;
        border-color: #2B3139 !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #1E2329 !important;
        border-color: #2B3139 !important;
    }
    .st-bd {border-color: #2B3139 !important;}
    .st-ax {background-color: #1E2329 !important;}

    /* ── expander ── */
    .streamlit-expanderHeader {
        background: #1E2329;
        border-radius: 8px;
        border: 1px solid #2B3139;
    }
    .streamlit-expanderHeader:hover {border-color: #F0B90B44;}

    /* ── 进度条覆盖 ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #F0B90B, #F5D76E) !important;
    }

    /* ── Toast 自定义 ── */
    div[data-testid="stToast"] {
        background: #1E2329 !important;
        border: 1px solid #F0B90B44 !important;
        border-radius: 10px !important;
    }

    /* ── Sidebar 底部 tip ── */
    .sidebar-tip {
        position: fixed;
        bottom: 0.5rem;
        left: 0.8rem;
        font-size: 0.65rem;
        color: #5E6673;
        padding: 0.2rem 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ── Session State 初始化 ──────────────────────────────────
# ══════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "🏠 首页"
if "selected_phase" not in st.session_state:
    st.session_state.selected_phase = None
if "selected_lab" not in st.session_state:
    st.session_state.selected_lab = None
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False


# ══════════════════════════════════════════════════════════════
# ── 辅助函数 ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

def metric_card(icon: str, value: str, label: str, delta: str = "") -> str:
    """返回一个仪表盘指标卡片 HTML"""
    delta_html = f'<div class="delta">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="icon">{icon}</div>
        <div class="num">{value}</div>
        <div class="label">{label}</div>
        {delta_html}
    </div>
    """


def status_badge(pct: float) -> str:
    """根据完成百分比返回 badges"""
    if pct >= 100:
        return '<span class="tc-badge completed">已完成</span>'
    elif pct > 0:
        return '<span class="tc-badge in-progress">进行中</span>'
    else:
        return '<span class="tc-badge not-started">未开始</span>'


def phase_card_html(phase_name: str, chapter_count: int, completed_pct: float,
                    phase_id: str, is_selected: bool = False) -> str:
    """知识/实践轨道的阶段卡片 HTML"""
    sel = " selected" if is_selected else ""
    badge = status_badge(completed_pct)
    return f"""
    <div class="track-card{sel}" data-phase="{phase_id}">
        <div class="tc-header">
            <span class="tc-name">{phase_name}</span>
            <span class="tc-count">{chapter_count}章</span>
        </div>
        <div class="tc-header" style="margin-top:0.25rem;">
            <span class="tc-count">完成 {completed_pct:.0f}%</span>
            {badge}
        </div>
        <div class="tc-bar-wrap">
            <div class="tc-bar-fill" style="width:{min(completed_pct,100)}%;"></div>
        </div>
    </div>
    """


def lab_card_html(lab_name: str, has_guide: bool, has_exercises: bool,
                  lab_id: str, is_selected: bool = False) -> str:
    """实验室卡片 HTML"""
    sel = " selected" if is_selected else ""

    # 推断难度（简单示意）
    if has_guide and has_exercises:
        difficulty = "中级"
        diff_cls = "in-progress"
    elif has_guide:
        difficulty = "入门"
        diff_cls = "completed"
    else:
        difficulty = "待开放"
        diff_cls = "not-started"

    status = "已就绪" if has_guide else "建设中"
    status_cls = "completed" if has_guide else "not-started"

    return f"""
    <div class="track-card{sel}" data-lab="{lab_id}">
        <div class="tc-header">
            <span class="tc-name">{lab_name}</span>
            <span class="tc-badge {diff_cls}" style="margin-left:0.6rem;">{difficulty}</span>
        </div>
        <div class="tc-header" style="margin-top:0.3rem;">
            <span class="tc-count">{'📖 有实验指南' if has_guide else '📖 指南待完善'}</span>
            <span class="tc-badge {status_cls}">{status}</span>
        </div>
    </div>
    """


def chapter_list_html(chapters: list[dict]) -> str:
    """渲染章节列表 HTML（带完成标记）"""
    rows = []
    for ch in chapters:
        icon = "✅" if ch.get("completed") else "📄"
        icon_cls = "done" if ch.get("completed") else "pending"
        rows.append(f"""
        <div class="ch-item">
            <span class="ch-icon {icon_cls}">{icon}</span>
            <span class="ch-title">{ch.get("title", ch.get("id",""))}</span>
        </div>
        """)
    return f'<div class="ch-list">{"".join(rows)}</div>'


def render_timeline_item(phase_label: str, topic: str, meta: str,
                         status: str = "") -> str:
    """渲染单个时间线条目"""
    dot_cls = "completed" if status == "completed" else ("active" if status == "active" else "")
    phase_cls = "completed" if status == "completed" else ""
    return f"""
    <div class="tl-item">
        <div class="tl-dot {dot_cls}"></div>
        <div class="tl-phase {phase_cls}">{phase_label}</div>
        <div class="tl-topic">{topic} <span class="tl-meta">{meta}</span></div>
    </div>
    """


# ══════════════════════════════════════════════════════════════
# ── 页面渲染函数 ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

def render_home():
    """首页 — Hero + 指标 + 继续学习 + 时间线 + 特性卡片"""
    # Hero
    st.markdown('<div class="hero-title">投资学院</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">从零基础到投资大拿 — 系统化掌握股市与投资知识</div>',
                unsafe_allow_html=True)

    # ── 统计指标 ──
    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception:
        all_progress = []

    completed_chs = [p for p in all_progress if p.get("completed")]
    total_chs = 34  # 课程总章节数

    # 测验均分
    avg_score = 0.0
    if completed_chs:
        scores = [p.get("quiz_score", 0.0) for p in completed_chs if p.get("quiz_score", 0.0) > 0]
        if scores:
            avg_score = sum(scores) / len(scores)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(metric_card("📖", f"{len(completed_chs)}/{total_chs}", "已完成章节",
                                f"完成率 {len(completed_chs)/max(total_chs,1)*100:.0f}%"),
                    unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("📊", f"{avg_score*100:.1f}", "测验均分",
                                "满分 100" if avg_score > 0 else ""),
                    unsafe_allow_html=True)
    with col3:
        # 粗略学习天数：按有进度的章节 count distinct 日期
        days = len(set(p.get("last_accessed", "")[:10] for p in all_progress if p.get("last_accessed")))
        st.markdown(metric_card("📅", f"{max(days, 1)}", "学习天数"),
                    unsafe_allow_html=True)

    # ── 继续学习按钮 ──
    current_phase = "p1_basics"
    try:
        from db.repository import get_user_preferences
        prefs = get_user_preferences()
        current_phase = prefs.get("current_phase", "p1_basics")
    except Exception:
        pass

    phase_display_map = {
        "p1_basics": "P1 股市基础",
        "p2_technical": "P2 技术分析入门",
        "p3_sectors": "P3 板块与产业链",
        "p4_quant": "P4 量化策略思维",
        "p5_risk": "P5 风险管理",
        "p6_psychology": "P6 交易心理与市场情绪",
        "p7_integration": "P7 实战整合",
        "p1": "P1 股市基础",
    }

    st.markdown(f"""
    <div class="continue-btn-wrap">
        <button class="continue-btn" onclick="
            const evt = new CustomEvent('streamlit:setComponentValue', {{
                detail: {{key: 'continue_clicked', value: true}}
            }});
            document.dispatchEvent(evt);
        ">
            ▶ 继续学习 — {phase_display_map.get(current_phase, current_phase)}
        </button>
    </div>
    """, unsafe_allow_html=True)

    # 监听 continue_clicked
    if st.button("▶ 继续学习", key="continue_btn_real", use_container_width=False):
        st.session_state.page = "📚 知识轨道"
        st.session_state.selected_phase = current_phase
        st.rerun()

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)

    # ── 学习路径时间线 ──
    st.markdown("### 🗺️ 学习路径")

    # 根据完成进度判断哪些阶段已完成
    completed_phase_ids = set()
    for p in all_progress:
        cid = p.get("chapter_id", "")
        if p.get("completed"):
            completed_phase_ids.add(cid.rsplit("_", 1)[0] if "_ch" in cid else cid)

    path_data = [
        ("P1 股市基础", "股票 / ETF / K线 / 交易规则", "5章 · 2天", "p1"),
        ("P2 技术分析", "趋势 / 微观结构 / 均线 / Wyckoff", "5章 · 3天", "p2"),
        ("P3 板块产业链", "行业分类 / 产业链 / 板块轮动", "4章 · 2天", "p3"),
        ("P4 量化策略", "概率思维 / 规则策略 / ML融合", "5章 · 3天", "p4"),
        ("P5 风险管理", "仓位 / 回撤 / 波动率 / 尾部风险", "5章 · 3天", "p5"),
        ("P6 交易心理", "情绪管理 / 认知偏差 / 市场情绪", "6章 · 3天", "p6"),
        ("P7 实战整合", "回测 / 偏差 / 完整交易系统", "4章 · 2天", "p7"),
    ]

    timeline_items = []
    for i, (label, topic, meta, pid) in enumerate(path_data):
        if pid in completed_phase_ids:
            status = "completed"
        elif i < 3:  # 前几个设为 active 示意
            status = "active"
        else:
            status = ""
        timeline_items.append(render_timeline_item(label, topic, meta, status))

    st.markdown(f'<div class="timeline">{"".join(timeline_items)}</div>',
                unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)

    # ── 特性卡片 ──
    st.markdown("### 🚀 快速开始")
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="fc-icon">📚</div>
            <div class="fc-title">知识轨道</div>
            <div class="fc-desc">7个阶段 · 34章系统学习，从股市基础概念到完整交易系统，循序渐进</div>
            <span class="fc-badge">新手推荐</span>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🔬</div>
            <div class="fc-title">实践轨道</div>
            <div class="fc-desc">6个实验室 · 动手探索，用真实市场数据理解每个概念的实际含义</div>
            <span class="fc-badge">动手实践</span>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🎮</div>
            <div class="fc-title">交易沙盒</div>
            <div class="fc-desc">零风险模拟交易，用历史数据练习决策，积累实战经验</div>
            <span class="fc-badge">即将上线</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_knowledge_track():
    """知识轨道 — 阶段卡片列表 + 章节内容"""
    st.markdown("### 📚 知识轨道")
    st.markdown('<p style="color:#848E9C;margin-bottom:1.2rem;">系统化学习股市投资的各个知识领域</p>',
                unsafe_allow_html=True)

    try:
        from interactive.content_loader import list_phases
        from db.repository import get_all_chapter_progress
        phases = list_phases()
        all_progress = get_all_chapter_progress()
    except Exception as e:
        st.error(f"加载知识轨道失败: {e}")
        return

    if not phases:
        st.info("暂无可用章节内容")
        return

    phase_names = {
        "p1_basics": "P1: 股市基础",
        "p2_technical": "P2: 技术分析入门",
        "p3_sectors": "P3: 板块与产业链",
        "p4_quant": "P4: 量化策略思维",
        "p5_risk": "P5: 风险管理",
        "p6_psychology": "P6: 交易心理与市场情绪",
        "p7_integration": "P7: 实战整合",
    }

    # 分组统计每个阶段的完成情况
    phase_progress_map: dict[str, list] = {}
    for p in all_progress:
        cid = p.get("chapter_id", "")
        # chapter_id 格式: p1_ch1 → phase_key = "p1_basics"
        prefix = cid.rsplit("_", 1)[0] if "_ch" in cid else cid
        phase_progress_map.setdefault(prefix, []).append(p)

    #  计算完成百分比
    def calc_pct(phase_id: str) -> float:
        chaps = phase_progress_map.get(phase_id, [])
        if not chaps:
            return 0.0
        done = sum(1 for c in chaps if c.get("completed"))
        return done / len(chaps) * 100

    col_left, col_right = st.columns([1, 1.8])

    with col_left:
        st.markdown("**选择阶段**")
        for p in phases:
            pid = p["id"]
            name = phase_names.get(pid, pid)
            cnt = p["chapter_count"]
            pct = calc_pct(pid)
            is_sel = (st.session_state.selected_phase == pid)

            # 用 st.markdown + 点击模拟
            st.markdown(phase_card_html(name, cnt, pct, pid, is_sel),
                        unsafe_allow_html=True)

            # 用列 + 按钮做卡片点击
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button(f"📖 {name.split(':')[0] if ':' in name else name}",
                             key=f"phase_btn_{pid}", use_container_width=True):
                    st.session_state.selected_phase = pid
                    st.rerun()

    with col_right:
        selected_id = st.session_state.selected_phase or phases[0]["id"]
        selected_name = phase_names.get(selected_id, selected_id)

        st.markdown(f"**{selected_name}**")

        # 通过 importlib 动态加载页面
        module_name = f"pages.knowledge.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"📝 {selected_name} 内容正在编写中…")
        except ImportError:
            st.info(f"📝 {selected_name} 内容正在编写中…")
        except Exception as e:
            st.error(f"加载页面出错: {e}")


def render_practice_track():
    """实践轨道 — 实验室卡片列表"""
    st.markdown("### 🔬 实践轨道")
    st.markdown('<p style="color:#848E9C;margin-bottom:1.2rem;">动手探索真实市场数据与交易策略</p>',
                unsafe_allow_html=True)

    try:
        from interactive.content_loader import list_labs
        labs = list_labs()
    except Exception as e:
        st.error(f"加载实践轨道失败: {e}")
        return

    if not labs:
        st.info("暂无可用实验")
        return

    lab_names = {
        "m1_data_lab": "M1: 数据勘探实验室",
        "m2_feature_lab": "M2: 特征工程实验室",
        "m3_prediction": "M3: 预测引擎探索",
        "m4_risk_sandbox": "M4: 风控沙盒",
        "m5_backtest": "M5: 回测分析器",
        "m6_sentiment": "M6: 市场情绪实验室",
    }

    # 左侧实验室列表
    col_left, col_right = st.columns([1, 1.8])

    with col_left:
        st.markdown("**选择实验室**")
        for lab in labs:
            lid = lab["id"]
            name = lab_names.get(lid, lid)
            has_guide = lab.get("has_guide", False)
            has_exercises = lab.get("has_exercises", False)
            is_sel = (st.session_state.selected_lab == lid)

            st.markdown(lab_card_html(name, has_guide, has_exercises, lid, is_sel),
                        unsafe_allow_html=True)

            if st.button(f"🔬 {name.split(':')[0] if ':' in name else name}",
                         key=f"lab_btn_{lid}", use_container_width=True):
                st.session_state.selected_lab = lid
                st.rerun()

    with col_right:
        selected_id = st.session_state.selected_lab or labs[0]["id"]
        selected_name = lab_names.get(selected_id, selected_id)
        st.markdown(f"**{selected_name}**")

        module_name = f"pages.practice.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"🔬 {selected_name} 正在建设中…")
        except ImportError:
            st.info(f"🔬 {selected_name} 正在建设中…")
        except Exception as e:
            st.error(f"加载实验室出错: {e}")


def render_sandbox():
    """交易沙盒 — 占位"""
    st.markdown("### 🎮 交易沙盒")
    st.markdown('<p style="color:#848E9C;margin-bottom:1rem;">零风险模拟真实交易环境</p>',
                unsafe_allow_html=True)

    # 带进度条的占位
    st.markdown("""
    <div class="track-card" style="cursor:default;">
        <div class="tc-header">
            <span class="tc-name">🚧 交易沙盒正在建设中</span>
            <span class="tc-badge in-progress">开发中</span>
        </div>
        <div style="margin-top:0.8rem;color:#848E9C;font-size:0.9rem;">
            完成后你将可以在这里用历史数据模拟真实交易决策，包括：<br>
            • 实时 K线 图表与多时间框架分析<br>
            • 自定义策略回测与绩效评估<br>
            • 风险控制模块（止损 / 仓位管理）<br>
            • 交易心理记录与复盘
        </div>
        <div class="tc-bar-wrap" style="margin-top:1rem;">
            <div class="tc-bar-fill" style="width:35%;"></div>
        </div>
        <div style="margin-top:0.3rem;font-size:0.75rem;color:#5E6673;">总体进度 35%</div>
    </div>
    """, unsafe_allow_html=True)


def render_progress():
    """学习进度 — 简版仪表盘"""
    st.markdown("### 📊 学习进度")
    st.markdown('<p style="color:#848E9C;margin-bottom:1rem;">查看你的学习统计与成就</p>',
                unsafe_allow_html=True)

    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception as e:
        st.error(f"加载进度数据失败: {e}")
        return

    completed = [p for p in all_progress if p.get("completed")]
    total = max(len(all_progress), 1)

    # 概览指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("📖", str(len(completed)), "已完成"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("📊", f"{len(completed)/total*100:.0f}%", "完成率"), unsafe_allow_html=True)
    with col3:
        scores = [p.get("quiz_score", 0) for p in completed if p.get("quiz_score", 0) > 0]
        avg = sum(scores) / len(scores) if scores else 0
        st.markdown(metric_card("🎯", f"{avg*100:.0f}%", "均分"), unsafe_allow_html=True)
    with col4:
        days = len(set(p.get("last_accessed", "")[:10] for p in all_progress if p.get("last_accessed")))
        st.markdown(metric_card("📅", str(max(days, 1)), "学习天数"), unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)

    # 最近学习记录
    st.markdown("**最近学习记录**")
    recent = sorted(all_progress, key=lambda x: x.get("last_accessed", ""), reverse=True)[:10]
    if recent:
        for r in recent:
            cid = r.get("chapter_id", "?")
            done = "✅" if r.get("completed") else "📄"
            score = f' 得分 {r.get("quiz_score", 0)*100:.0f}%' if r.get("quiz_score", 0) > 0 else ""
            date = (r.get("last_accessed", "")[:10] or "—") if r.get("last_accessed") else "—"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.8rem;padding:0.3rem 0.6rem;
                        border-bottom:1px solid #2B3139;font-size:0.88rem;">
                <span>{done}</span>
                <span style="flex:1;color:#EAECEF;">{cid}</span>
                <span style="color:#848E9C;font-size:0.8rem;">{score}</span>
                <span style="color:#5E6673;font-size:0.75rem;">{date}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有学习记录，快去开始学习吧！")


# ══════════════════════════════════════════════════════════════
# ── 侧边栏 ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <span style="font-size:2.5rem;">📈</span>
        <h2 style="margin:0.2rem 0 0;letter-spacing:0.1em;">投资学院</h2>
        <p style="font-size:0.75rem;color:#848E9C;margin:0;">Systematic Path to Alpha</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)

    # 导航
    nav_items = {
        "🏠 首页": "🏠 首页",
        "📚 知识轨道": "📚 知识轨道",
        "🔬 实践轨道": "🔬 实践轨道",
        "🎮 交易沙盒": "🎮 交易沙盒",
        "📊 学习进度": "📊 学习进度",
    }

    selected = st.radio(
        "导航",
        list(nav_items.keys()),
        label_visibility="collapsed",
        index=list(nav_items.keys()).index(st.session_state.page)
        if st.session_state.page in nav_items else 0,
    )
    st.session_state.page = selected

    st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)

    # ── 快捷统计 ──
    try:
        from db.repository import get_all_chapter_progress
        sp = get_all_chapter_progress()
        done = sum(1 for p in sp if p.get("completed"))
        scores = [p.get("quiz_score", 0) for p in sp if p.get("quiz_score", 0) > 0]
        avg_q = f"{sum(scores)/len(scores)*100:.0f}%" if scores else "—"
    except Exception:
        done = 0
        avg_q = "—"

    st.markdown(f"""
    <div style="padding:0.2rem 0;">
        <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:0.25rem 0;">
            <span style="color:#848E9C;">已完成章节</span>
            <span style="color:#F0B90B;font-weight:700;">{done}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:0.25rem 0;">
            <span style="color:#848E9C;">测验均分</span>
            <span style="color:#F0B90B;font-weight:700;">{avg_q}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 底部提示 ──
    st.markdown("""
    <div class="sidebar-tip">⌨ 按 Ctrl+C 停止</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ── Toast 欢迎 ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

if not st.session_state.welcome_shown:
    st.toast("🎉 欢迎回到投资学院！继续你的学习之旅吧。")
    st.session_state.welcome_shown = True


# ══════════════════════════════════════════════════════════════
# ── 路由 ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

page = st.session_state.page

if page == "🏠 首页":
    render_home()
elif page == "📚 知识轨道":
    render_knowledge_track()
elif page == "🔬 实践轨道":
    render_practice_track()
elif page == "🎮 交易沙盒":
    render_sandbox()
elif page == "📊 学习进度":
    render_progress()
