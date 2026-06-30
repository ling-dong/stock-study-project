"""投资学院 — Streamlit 主入口（Dark OLED Luxury）"""
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
# ── 全局 CSS — Dark OLED Luxury ───────────────────────────
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ════════════════════════════════════════
       Base — deep black, dot grid
       ════════════════════════════════════════ */
    .stApp {
        background: #0A0A0B;
        background-image: radial-gradient(circle, #1A1A1D 1px, transparent 1px);
        background-size: 24px 24px;
    }
    .main > div {
        background: transparent;
        padding: 0 1.8rem 3rem;
    }
    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    /* Scrollbar */
    ::-webkit-scrollbar {width: 5px; height: 5px;}
    ::-webkit-scrollbar-track {background: #0A0A0B;}
    ::-webkit-scrollbar-thumb {background: #F0B90B33; border-radius: 4px;}
    ::-webkit-scrollbar-thumb:hover {background: #F0B90B66;}

    /* ════════════════════════════════════════
       Typography
       ════════════════════════════════════════ */
    h1, h2, h3, h4, h5, h6 {
        color: #F5F0E0 !important;
        letter-spacing: 0.03em;
        font-weight: 300 !important;
    }
    h1 {font-size: 2.6rem !important; font-weight: 200 !important; margin-bottom: 0.2rem !important;}
    h2 {font-size: 1.6rem !important; font-weight: 300 !important; margin-top: 1.8rem !important;}
    h3 {font-size: 1.15rem !important; font-weight: 400 !important;}
    p, li, div, span, label {
        color: #E8E6E3;
    }
    a {
        color: #F0B90B !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }

    /* ════════════════════════════════════════
       Hero
       ════════════════════════════════════════ */
    .hero-section {
        margin-bottom: 2.5rem;
        margin-top: 1rem;
    }
    .hero-eyebrow {
        font-size: 0.7rem;
        letter-spacing: 0.25em;
        color: #6B6B7B;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 200;
        color: #F5F0E0;
        margin-bottom: 0.4rem;
        line-height: 1.15;
        letter-spacing: 0.02em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #8B8B9E;
        margin-bottom: 1.8rem;
        font-weight: 300;
    }

    /* ════════════════════════════════════════
       Metrics Row — data first
       ════════════════════════════════════════ */
    .metrics-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        flex: 1;
        background: #141417;
        border: 1px solid #252529;
        border-radius: 12px;
        padding: 1.4rem 1.2rem 1.1rem;
        text-align: center;
        transition: border-color 0.3s, box-shadow 0.3s, transform 0.25s;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; height: 100%; width: 3px;
        background: linear-gradient(180deg, #F0B90B, #F0B90B00);
        opacity: 0;
        transition: opacity 0.35s;
    }
    .metric-card:hover {
        border-color: #3A3A45;
        box-shadow: 0 8px 40px rgba(0,0,0,0.5);
        transform: translateY(-2px);
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-card .mc-icon {
        font-size: 1.4rem;
        line-height: 1;
        margin-bottom: 0.3rem;
        opacity: 0.6;
    }
    .metric-card .mc-value {
        font-size: 2.6rem;
        font-weight: 200;
        color: #F5F0E0;
        margin: 0.1rem 0;
        line-height: 1.1;
        letter-spacing: 0.01em;
    }
    .metric-card .mc-label {
        font-size: 0.75rem;
        color: #6B6B7B;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 400;
    }
    .metric-card .mc-delta {
        font-size: 0.7rem;
        color: #4CAF50;
        margin-top: 0.15rem;
    }

    /* ════════════════════════════════════════
       Gold Divider — left-fade gradient
       ════════════════════════════════════════ */
    .gold-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, #F0B90B, #F0B90B22, transparent);
        margin: 1.8rem 0;
    }

    /* ════════════════════════════════════════
       Section Header
       ════════════════════════════════════════ */
    .section-header {
        margin-bottom: 1.2rem;
    }
    .section-header h2 {
        font-size: 1.4rem !important;
        font-weight: 300 !important;
        margin: 0 !important;
        border: none !important;
        padding: 0 !important;
    }
    .section-header p {
        font-size: 0.85rem;
        color: #6B6B7B;
        margin: 0.15rem 0 0 0;
    }

    /* ════════════════════════════════════════
       Glass Card
       ════════════════════════════════════════ */
    .glass-card {
        background: #141417;
        border: 1px solid #252529;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s;
    }
    .glass-card:hover {
        border-color: #3A3A45;
        box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    }

    /* ════════════════════════════════════════
       Timeline
       ════════════════════════════════════════ */
    .timeline {
        position: relative;
        padding-left: 2.2rem;
        margin: 1.2rem 0 0.5rem;
    }
    .timeline::before {
        content: "";
        position: absolute;
        left: 7px;
        top: 0;
        bottom: 0;
        width: 1px;
        background: linear-gradient(180deg, #F0B90B55, #F0B90B11, transparent);
    }
    .tl-item {
        position: relative;
        padding: 0.5rem 0 0.5rem 1.4rem;
        transition: background 0.2s;
        border-radius: 6px;
    }
    .tl-item:not(:last-child) {margin-bottom: 0.1rem;}
    .tl-dot {
        position: absolute;
        left: -1.95rem;
        top: 0.7rem;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3A3A45;
        border: 2px solid #0A0A0B;
        transition: all 0.3s;
    }
    .tl-dot.completed {
        background: #4CAF50;
        box-shadow: 0 0 0 3px #4CAF5033;
    }
    .tl-dot.active {
        background: #F0B90B;
        box-shadow: 0 0 0 4px #F0B90B33;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    .tl-phase {
        font-weight: 350;
        color: #F5F0E0;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
    }
    .tl-phase.completed {
        color: #4CAF50;
    }
    .tl-topic {
        font-size: 0.78rem;
        color: #6B6B7B;
    }
    .tl-meta {
        font-size: 0.7rem;
        color: #4A4A55;
        margin-left: 0.5rem;
    }
    @keyframes pulse-dot {
        0%, 100% {box-shadow: 0 0 0 4px #F0B90B33;}
        50% {box-shadow: 0 0 0 8px #F0B90B15;}
    }

    /* ════════════════════════════════════════
       Feature Cards (Home grid)
       ════════════════════════════════════════ */
    .feature-grid {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 0.5rem 0 1.5rem;
    }
    .feature-card {
        flex: 1;
        min-width: 220px;
        background: #141417;
        border: 1px solid #252529;
        border-radius: 12px;
        padding: 1.6rem;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #F0B90B, #F0B90B00);
        opacity: 0;
        transition: opacity 0.35s;
    }
    .feature-card:hover {
        border-color: #3A3A45;
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(0,0,0,0.5);
    }
    .feature-card:hover::before {
        opacity: 1;
    }
    .feature-card .fc-icon {
        font-size: 1.8rem;
        line-height: 1;
        opacity: 0.7;
    }
    .feature-card .fc-title {
        font-size: 1.05rem;
        font-weight: 400;
        color: #F5F0E0;
        margin: 0.6rem 0 0.3rem;
    }
    .feature-card .fc-desc {
        font-size: 0.82rem;
        color: #6B6B7B;
        line-height: 1.55;
    }
    .feature-card .fc-badge {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 500;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        margin-top: 0.7rem;
        background: #F0B90B12;
        color: #F0B90B;
        border: 1px solid #F0B90B25;
    }

    /* ════════════════════════════════════════
       Continue button — gold pill
       ════════════════════════════════════════ */
    .continue-btn-wrap {
        display: flex;
        justify-content: flex-start;
        margin: 0.8rem 0 1.5rem;
    }
    .continue-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: transparent;
        color: #F0B90B !important;
        font-weight: 400;
        font-size: 0.85rem;
        padding: 0.5rem 1.4rem;
        border-radius: 40px;
        border: 1px solid #F0B90B33;
        transition: all 0.3s;
        cursor: default;
        letter-spacing: 0.04em;
    }
    .continue-btn:hover {
        border-color: #F0B90B66;
        box-shadow: 0 0 24px rgba(240,185,11,0.08);
    }

    /* ════════════════════════════════════════
       Phase Pills — horizontal tab bar
       ════════════════════════════════════════ */
    .phase-pills {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid #1A1A1D;
    }
    .phase-pill {
        padding: 0.4rem 1rem;
        font-size: 0.8rem;
        border-radius: 20px;
        background: transparent;
        color: #6B6B7B;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.25s;
        font-weight: 350;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }
    .phase-pill:hover {
        color: #F5F0E0;
        background: #141417;
        border-color: #252529;
    }
    .phase-pill.active {
        color: #F0B90B;
        background: #F0B90B12;
        border-color: #F0B90B33;
    }
    .phase-pill .pill-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-right: 0.4rem;
        vertical-align: middle;
    }
    .pill-dot.completed { background: #4CAF50; }
    .pill-dot.in-progress { background: #F0B90B; }
    .pill-dot.not-started { background: #3A3A45; }

    /* ════════════════════════════════════════
       Content cards (knowledge / practice list)
       ════════════════════════════════════════ */
    .track-card {
        background: #141417;
        border: 1px solid #252529;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.7rem;
        cursor: pointer;
        transition: all 0.25s;
        position: relative;
        overflow: hidden;
    }
    .track-card::before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #F0B90B, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .track-card:hover {
        border-color: #3A3A45;
        box-shadow: 0 6px 28px rgba(0,0,0,0.4);
    }
    .track-card:hover::before {
        opacity: 1;
    }
    .track-card.selected {
        border-color: #F0B90B44;
    }
    .track-card.selected::before {
        opacity: 1;
    }
    .track-card .tc-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .track-card .tc-name {
        font-size: 0.95rem;
        font-weight: 400;
        color: #F5F0E0;
    }
    .track-card .tc-count {
        font-size: 0.72rem;
        color: #6B6B7B;
    }
    .track-card .tc-bar-wrap {
        margin-top: 0.45rem;
        height: 3px;
        background: #1A1A1D;
        border-radius: 2px;
        overflow: hidden;
    }
    .track-card .tc-bar-fill {
        height: 100%;
        border-radius: 2px;
        background: linear-gradient(90deg, #F0B90B, #F5F0E066);
        transition: width 0.6s ease;
    }
    .tc-badge {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 500;
        padding: 0.15rem 0.65rem;
        border-radius: 20px;
        border: 1px solid;
    }
    .tc-badge.not-started {
        background: transparent;
        color: #4A4A55;
        border-color: #252529;
    }
    .tc-badge.in-progress {
        background: #F0B90B0E;
        color: #F0B90B;
        border-color: #F0B90B25;
    }
    .tc-badge.completed {
        background: #4CAF500E;
        color: #4CAF50;
        border-color: #4CAF5025;
    }

    /* ════════════════════════════════════════
       Chapter list items
       ════════════════════════════════════════ */
    .ch-list {margin: 0.8rem 0;}
    .ch-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.4rem 0.6rem;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .ch-item:hover {background: #141417;}
    .ch-item .ch-icon {font-size: 1rem; width: 1.3rem; text-align: center;}
    .ch-item .ch-icon.done {color: #4CAF50;}
    .ch-item .ch-icon.pending {color: #4A4A55;}
    .ch-item .ch-title {
        font-size: 0.85rem;
        color: #E8E6E3;
        flex: 1;
        font-weight: 300;
    }

    /* ════════════════════════════════════════
       Sidebar — darker glass
       ════════════════════════════════════════ */
    .stSidebar {
        background: #050506 !important;
        border-right: 1px solid #151518;
    }
    .stSidebar .sidebar-content {
        background: #050506;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background: #050506;
    }
    .stSidebar hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #252529, transparent);
        margin: 0.8rem 0;
    }
    .sidebar-profile {
        text-align: center;
        padding: 1.2rem 0.5rem 0.3rem;
    }
    .sidebar-profile .sp-icon {
        font-size: 2.2rem;
        line-height: 1;
        opacity: 0.8;
    }
    .sidebar-profile .sp-title {
        font-size: 0.95rem;
        font-weight: 300;
        color: #F5F0E0;
        margin: 0.2rem 0 0;
        letter-spacing: 0.12em;
    }
    .sidebar-profile .sp-sub {
        font-size: 0.65rem;
        color: #4A4A55;
        margin: 0;
        letter-spacing: 0.06em;
    }

    /* Sidebar nav radio override */
    .stSidebar div[data-testid="stVerticalBlock"] > div > div > label {
        padding: 0.35rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
        font-size: 0.85rem !important;
        font-weight: 300 !important;
    }
    .stSidebar div[data-testid="stVerticalBlock"] > div > div > label:hover {
        background: #141417 !important;
    }
    .stSidebar div[data-testid="stVerticalBlock"] > div > div > label[data-selected="true"] {
        background: #F0B90B0A !important;
        color: #F0B90B !important;
        border-left: 2px solid #F0B90B;
        border-radius: 0 8px 8px 0 !important;
    }

    /* Sidebar stats */
    .sidebar-stats {
        padding: 0.2rem 0.3rem;
    }
    .sidebar-stats .ss-row {
        display: flex;
        justify-content: space-between;
        padding: 0.3rem 0;
        font-size: 0.78rem;
    }
    .sidebar-stats .ss-label {
        color: #4A4A55;
    }
    .sidebar-stats .ss-value {
        color: #F5F0E0;
        font-weight: 350;
    }

    /* Sidebar footer tip */
    .sidebar-footer {
        position: fixed;
        bottom: 0.6rem;
        left: 1rem;
        font-size: 0.6rem;
        color: #3A3A45;
        letter-spacing: 0.06em;
    }

    /* ════════════════════════════════════════
       Button overrides
       ════════════════════════════════════════ */
    .stButton > button {
        background: transparent !important;
        color: #F0B90B !important;
        font-weight: 350 !important;
        border-radius: 40px !important;
        border: 1px solid #F0B90B33 !important;
        padding: 0.3rem 1.6rem !important;
        transition: all 0.25s !important;
        font-size: 0.8rem !important;
    }
    .stButton > button:hover {
        border-color: #F0B90B66 !important;
        box-shadow: 0 0 24px rgba(240,185,11,0.06) !important;
        background: #F0B90B06 !important;
    }

    /* ════════════════════════════════════════
       Alert / Info / Success / Warning
       ════════════════════════════════════════ */
    div[data-testid="stAlert"] {
        background: #141417 !important;
        border: 1px solid #252529 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] > div:first-child {
        background: transparent !important;
        border: none !important;
    }

    /* ════════════════════════════════════════
       Select / Input
       ════════════════════════════════════════ */
    div[data-baseweb="select"] > div {
        background-color: #141417 !important;
        border-color: #252529 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #141417 !important;
        border-color: #252529 !important;
        border-radius: 8px !important;
    }
    .st-bd {border-color: #252529 !important;}
    .st-ax {background-color: #141417 !important;}

    /* Select dropdown */
    div[data-baseweb="popover"] ul {
        background: #141417 !important;
        border: 1px solid #252529 !important;
    }

    /* ════════════════════════════════════════
       Progress bar
       ════════════════════════════════════════ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #F0B90B, #F5F0E055) !important;
    }
    .stProgress > div > div {
        background: #1A1A1D !important;
    }

    /* ════════════════════════════════════════
       Expander
       ════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: #141417;
        border-radius: 8px;
        border: 1px solid #252529;
        color: #E8E6E3 !important;
        font-weight: 300;
    }
    .streamlit-expanderHeader:hover {
        border-color: #3A3A45;
    }

    /* ════════════════════════════════════════
       Toast
       ════════════════════════════════════════ */
    div[data-testid="stToast"] {
        background: #141417 !important;
        border: 1px solid #F0B90B33 !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 40px rgba(0,0,0,0.6) !important;
    }

    /* ════════════════════════════════════════
       DataFrame
       ════════════════════════════════════════ */
    div[data-testid="stDataFrame"] {
        background: #141417 !important;
        border: 1px solid #252529 !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] th {
        background: #0A0A0B !important;
        color: #6B6B7B !important;
        font-weight: 400 !important;
        font-size: 0.75rem !important;
        border-bottom: 1px solid #252529 !important;
    }
    div[data-testid="stDataFrame"] td {
        color: #E8E6E3 !important;
        border-bottom: 1px solid #1A1A1D !important;
        font-size: 0.8rem !important;
    }

    /* ════════════════════════════════════════
       Tabs
       ════════════════════════════════════════ */
    div[data-testid="stTabs"] button {
        color: #6B6B7B !important;
        font-weight: 300 !important;
        font-size: 0.85rem !important;
        border-bottom: 1px solid transparent !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #F0B90B !important;
        border-bottom: 1px solid #F0B90B !important;
    }

    /* ════════════════════════════════════════
       Responsive tweaks
       ════════════════════════════════════════ */
    @media (max-width: 768px) {
        .metrics-row {
            flex-direction: column;
        }
        .feature-grid {
            flex-direction: column;
        }
        .hero-title {
            font-size: 2rem;
        }
        .main > div {
            padding: 0 1rem 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ── Session State 初始化 ──────────────────────────────────
# ══════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "首页"
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
    delta_html = f'<div class="mc-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="mc-icon">{icon}</div>
        <div class="mc-value">{value}</div>
        <div class="mc-label">{label}</div>
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


def phase_pill_html(phase_name: str, phase_id: str, status: str, is_active: bool = False) -> str:
    """Horizontal pill tab HTML"""
    dot_cls = "completed" if status == "completed" else ("in-progress" if status == "in-progress" else "not-started")
    active_cls = " active" if is_active else ""
    return f"""
    <div class="phase-pill{active_cls}" data-phase="{phase_id}">
        <span class="pill-dot {dot_cls}"></span>{phase_name}
    </div>
    """


def phase_card_html(phase_name: str, chapter_count: int, completed_pct: float,
                    phase_id: str, is_selected: bool = False) -> str:
    """知识/实践轨道的阶段卡片 HTML"""
    sel = " selected" if is_selected else ""
    badge = status_badge(completed_pct)
    return f"""
    <div class="track-card{sel}" data-phase="{phase_id}">
        <div class="tc-header">
            <span class="tc-name">{phase_name}</span>
            <span class="tc-count">{chapter_count} 章</span>
        </div>
        <div class="tc-header" style="margin-top:0.2rem;">
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
        <div class="tc-header" style="margin-top:0.25rem;">
            <span class="tc-count">{'有实验指南' if has_guide else '指南待完善'}</span>
            <span class="tc-badge {status_cls}">{status}</span>
        </div>
    </div>
    """


def chapter_list_html(chapters: list[dict]) -> str:
    """渲染章节列表 HTML（带完成标记）"""
    rows = []
    for ch in chapters:
        icon = "✓" if ch.get("completed") else "○"
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
    """首页 — Hero + 指标数据 + 继续学习 + 时间线 + 特性卡片"""

    # Hero
    st.markdown("""
    <div class="hero-section">
        <p class="hero-eyebrow">INVESTMENT ACADEMY</p>
        <h1 class="hero-title">从零到投资大拿</h1>
        <p class="hero-subtitle">系统化掌握股市知识，用真实数据积累实战经验</p>
    </div>
    """, unsafe_allow_html=True)

    # 统计指标
    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception:
        all_progress = []

    completed_chs = [p for p in all_progress if p.get("completed")]
    total_chs = 34

    avg_score = 0.0
    if completed_chs:
        scores = [p.get("quiz_score", 0.0) for p in completed_chs if p.get("quiz_score", 0.0) > 0]
        if scores:
            avg_score = sum(scores) / len(scores)

    days = len(set(p.get("last_accessed", "")[:10] for p in all_progress if p.get("last_accessed")))

    st.markdown(f"""
    <div class="metrics-row">
        {metric_card("📖", f"{len(completed_chs)} / {total_chs}", "已完成章节", f"完成率 {len(completed_chs)/max(total_chs,1)*100:.0f}%")}
        {metric_card("📊", f"{avg_score*100:.1f}" if avg_score > 0 else "—", "测验均分", "满分 100" if avg_score > 0 else "")}
        {metric_card("📅", f"{max(days, 1)}", "学习天数")}
    </div>
    """, unsafe_allow_html=True)

    # 继续学习
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
        <span class="continue-btn">→ 继续学习 — {phase_display_map.get(current_phase, current_phase)}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("继续学习", key="continue_btn", use_container_width=False):
        st.session_state.page = "知识轨道"
        st.session_state.selected_phase = current_phase
        st.rerun()

    # Gold Divider
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # 学习路径时间线
    st.markdown("""
    <div class="section-header">
        <h2>学习路径</h2>
        <p>7 个阶段，34 章，从基础概念到完整交易系统</p>
    </div>
    """, unsafe_allow_html=True)

    completed_phase_ids = set()
    if all_progress:
        completed_phase_ids = set()
        for p in all_progress:
            cid = p.get("chapter_id", "")
            if p.get("completed"):
                completed_phase_ids.add(cid.rsplit("_", 1)[0] if "_ch" in cid else cid)

    path_data = [
        ("P1 股市基础", "股票 / ETF / K 线 / 交易规则", "5 章", "p1"),
        ("P2 技术分析", "趋势 / 微观结构 / 均线 / Wyckoff", "5 章", "p2"),
        ("P3 板块产业链", "行业分类 / 产业链 / 板块轮动", "4 章", "p3"),
        ("P4 量化策略", "概率思维 / 规则策略 / ML 融合", "5 章", "p4"),
        ("P5 风险管理", "仓位 / 回撤 / 波动率 / 尾部风险", "5 章", "p5"),
        ("P6 交易心理", "情绪管理 / 认知偏差 / 市场情绪", "6 章", "p6"),
        ("P7 实战整合", "回测 / 偏差 / 完整交易系统", "4 章", "p7"),
    ]

    timeline_items = []
    for i, (label, topic, meta, pid) in enumerate(path_data):
        if pid in completed_phase_ids:
            status = "completed"
        elif i < 3:
            status = "active"
        else:
            status = ""
        timeline_items.append(render_timeline_item(label, topic, meta, status))

    st.markdown(f'<div class="timeline">{"".join(timeline_items)}</div>',
                unsafe_allow_html=True)

    # Gold Divider
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # 特性卡片
    st.markdown("""
    <div class="section-header">
        <h2>快速开始</h2>
        <p>选择你的学习方式</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="fc-icon">📚</div>
            <div class="fc-title">知识轨道</div>
            <div class="fc-desc">7 个阶段 · 34 章系统学习，从股市基础概念到完整交易系统</div>
            <span class="fc-badge">新手推荐</span>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🔬</div>
            <div class="fc-title">实践轨道</div>
            <div class="fc-desc">动手探索真实市场数据，用实践理解每个知识概念</div>
            <span class="fc-badge">动手实践</span>
        </div>
        <div class="feature-card">
            <div class="fc-icon">🎮</div>
            <div class="fc-title">交易沙盒</div>
            <div class="fc-desc">零风险模拟交易，用历史数据练习决策，积累经验</div>
            <span class="fc-badge">实战模拟</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_knowledge_track():
    """知识轨道 — 阶段卡片 + 章节内容"""
    st.markdown("""
    <div class="section-header">
        <h2>知识轨道</h2>
        <p>系统化学习股市投资的各个知识领域</p>
    </div>
    """, unsafe_allow_html=True)

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
        "p1_basics": "P1 股市基础",
        "p2_technical": "P2 技术分析入门",
        "p3_sectors": "P3 板块与产业链",
        "p4_quant": "P4 量化策略思维",
        "p5_risk": "P5 风险管理",
        "p6_psychology": "P6 交易心理与市场情绪",
        "p7_integration": "P7 实战整合",
    }

    # 阶段进度
    phase_progress_map: dict[str, list] = {}
    for p in all_progress:
        cid = p.get("chapter_id", "")
        prefix = cid.rsplit("_", 1)[0] if "_ch" in cid else cid
        phase_progress_map.setdefault(prefix, []).append(p)

    def calc_pct(phase_id: str) -> float:
        chaps = phase_progress_map.get(phase_id, [])
        if not chaps:
            return 0.0
        done = sum(1 for c in chaps if c.get("completed"))
        return done / len(chaps) * 100

    # Phase Pills (horizontal tab bar)
    pill_html = '<div class="phase-pills">'
    for p in phases:
        pid = p["id"]
        name = phase_names.get(pid, pid)
        pct = calc_pct(pid)
        if pct >= 100:
            status = "completed"
        elif pct > 0:
            status = "in-progress"
        else:
            status = "not-started"
        is_active = (st.session_state.selected_phase == pid)
        pill_html += phase_pill_html(name, pid, status, is_active)
    pill_html += '</div>'
    st.markdown(pill_html, unsafe_allow_html=True)

    # Phase pill buttons (hidden, used for click handling)
    pill_cols = st.columns(len(phases))
    for idx, p in enumerate(phases):
        pid = p["id"]
        name = phase_names.get(pid, pid)
        with pill_cols[idx]:
            if st.button(name, key=f"pill_{pid}", use_container_width=True):
                st.session_state.selected_phase = pid
                st.rerun()

    # Content area
    selected_id = st.session_state.selected_phase or phases[0]["id"]
    selected_name = phase_names.get(selected_id, selected_id)

    # Phase detail card
    pct = calc_pct(selected_id)
    chaps = phase_progress_map.get(selected_id, [])
    cnt = next((p["chapter_count"] for p in phases if p["id"] == selected_id), len(chaps))

    st.markdown(f"""
    <div class="track-card selected" style="cursor:default;">
        <div class="tc-header">
            <span class="tc-name" style="font-size:1.05rem;">{selected_name}</span>
            <span class="tc-count">{cnt} 章</span>
        </div>
        <div class="tc-header" style="margin-top:0.2rem;">
            <span class="tc-count">完成 {pct:.0f}%</span>
            {status_badge(pct)}
        </div>
        <div class="tc-bar-wrap">
            <div class="tc-bar-fill" style="width:{min(pct,100)}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 通过 importlib 动态加载页面
    module_name = f"pages.knowledge.{selected_id}"
    try:
        import importlib
        mod = importlib.import_module(module_name)
        if hasattr(mod, "show"):
            mod.show()
        else:
            st.info(f"内容正在编写中…")
    except ImportError:
        st.info(f"内容正在编写中…")
    except Exception as e:
        st.error(f"加载页面出错: {e}")


def render_practice_track():
    """实践轨道 — 实验室卡片列表"""
    st.markdown("""
    <div class="section-header">
        <h2>实践轨道</h2>
        <p>动手探索真实市场数据与交易策略</p>
    </div>
    """, unsafe_allow_html=True)

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
        "m1_data_lab": "M1 数据勘探实验室",
        "m2_feature_lab": "M2 特征工程实验室",
        "m3_prediction": "M3 预测引擎探索",
        "m4_risk_sandbox": "M4 风控沙盒",
        "m5_backtest": "M5 回测分析器",
        "m6_sentiment": "M6 市场情绪实验室",
    }

    # Phase pills for labs
    pill_html = '<div class="phase-pills">'
    for lab in labs:
        lid = lab["id"]
        name = lab_names.get(lid, lid)
        has_guide = lab.get("has_guide", False)
        status = "completed" if has_guide else "not-started"
        is_active = (st.session_state.selected_lab == lid)
        pill_html += phase_pill_html(name, lid, status, is_active)
    pill_html += '</div>'
    st.markdown(pill_html, unsafe_allow_html=True)

    # Hidden buttons for lab pills
    lab_cols = st.columns(len(labs))
    for idx, lab in enumerate(labs):
        lid = lab["id"]
        name = lab_names.get(lid, lid)
        with lab_cols[idx]:
            if st.button(name, key=f"labpill_{lid}", use_container_width=True):
                st.session_state.selected_lab = lid
                st.rerun()

    # Content area
    selected_id = st.session_state.selected_lab or labs[0]["id"]
    selected_name = lab_names.get(selected_id, selected_id)

    selected_lab = next((l for l in labs if l["id"] == selected_id), labs[0])
    has_guide = selected_lab.get("has_guide", False)

    st.markdown(f"""
    <div class="track-card selected" style="cursor:default;">
        <div class="tc-header">
            <span class="tc-name" style="font-size:1.05rem;">{selected_name}</span>
            <span class="tc-badge {'completed' if has_guide else 'not-started'}">{'已就绪' if has_guide else '建设中'}</span>
        </div>
        <div class="tc-header" style="margin-top:0.2rem;">
            <span class="tc-count">{'有实验指南' if has_guide else '指南待完善'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    module_name = f"pages.practice.{selected_id}"
    try:
        import importlib
        mod = importlib.import_module(module_name)
        if hasattr(mod, "show"):
            mod.show()
        else:
            st.info(f"正在建设中…")
    except ImportError:
        st.info(f"正在建设中…")
    except Exception as e:
        st.error(f"加载实验室出错: {e}")


def render_sandbox():
    """交易沙盒 — 功能化交易模拟器"""
    st.markdown("""
    <div class="section-header">
        <h2>交易沙盒</h2>
        <p>零风险模拟真实交易环境</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        from pages.sandbox import show as show_sandbox
        show_sandbox()
    except ImportError:
        # 占位内容 — 沙盒模块尚未创建
        st.markdown("""
        <div class="track-card" style="cursor:default;">
            <div class="tc-header">
                <span class="tc-name">交易沙盒</span>
                <span class="tc-badge in-progress">开发中</span>
            </div>
            <div style="margin-top:0.8rem;color:#6B6B7B;font-size:0.85rem;line-height:1.7;">
                完成后你将可以在这里用历史数据模拟真实交易决策：<br>
                • 实时 K 线图表与多时间框架分析<br>
                • 自定义策略回测与绩效评估<br>
                • 风险控制模块（止损 / 仓位管理）<br>
                • 交易心理记录与复盘
            </div>
            <div class="tc-bar-wrap" style="margin-top:1rem;">
                <div class="tc-bar-fill" style="width:35%;"></div>
            </div>
            <div style="margin-top:0.25rem;font-size:0.7rem;color:#4A4A55;">总体进度 35%</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("初始化沙盒数据", use_container_width=True):
                st.info("沙盒数据功能即将开放")
        with col2:
            if st.button("加载示例策略", use_container_width=True):
                st.info("示例策略功能即将开放")
    except Exception as e:
        st.error(f"加载交易沙盒失败: {e}")
        st.markdown("""
        <div class="track-card" style="cursor:default;">
            <div class="tc-header">
                <span class="tc-name">交易沙盒</span>
                <span class="tc-badge not-started">暂不可用</span>
            </div>
            <div style="margin-top:0.8rem;color:#6B6B7B;font-size:0.85rem;">
                沙盒模块遇到加载错误，请联系管理员。
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_progress():
    """学习进度 — 数据仪表盘"""
    st.markdown("""
    <div class="section-header">
        <h2>学习进度</h2>
        <p>查看你的学习统计与成就</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception as e:
        st.error(f"加载进度数据失败: {e}")
        return

    completed = [p for p in all_progress if p.get("completed")]
    total = max(len(all_progress), 1)

    scores = [p.get("quiz_score", 0) for p in completed if p.get("quiz_score", 0) > 0]
    avg = sum(scores) / len(scores) if scores else 0
    days = len(set(p.get("last_accessed", "")[:10] for p in all_progress if p.get("last_accessed")))

    st.markdown(f"""
    <div class="metrics-row">
        {metric_card("📖", str(len(completed)), "已完成")}
        {metric_card("📊", f"{len(completed)/total*100:.0f}%", "完成率")}
        {metric_card("🎯", f"{avg*100:.0f}%" if avg > 0 else "—", "均分")}
        {metric_card("📅", str(max(days, 1)), "学习天数")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # 最近学习记录
    st.markdown("""
    <div class="section-header">
        <h2>最近学习记录</h2>
    </div>
    """, unsafe_allow_html=True)

    recent = sorted(all_progress, key=lambda x: x.get("last_accessed", ""), reverse=True)[:10]
    if recent:
        for r in recent:
            cid = r.get("chapter_id", "?")
            done = "✓" if r.get("completed") else "○"
            score = f'得分 {r.get("quiz_score", 0)*100:.0f}%' if r.get("quiz_score", 0) > 0 else ""
            date = (r.get("last_accessed", "")[:10] or "—") if r.get("last_accessed") else "—"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.8rem;padding:0.4rem 0.6rem;
                        border-bottom:1px solid #1A1A1D;font-size:0.85rem;">
                <span style="color:{'#4CAF50' if r.get('completed') else '#4A4A55'};">{done}</span>
                <span style="flex:1;color:#E8E6E3;font-weight:300;">{cid}</span>
                <span style="color:#6B6B7B;font-size:0.78rem;">{score}</span>
                <span style="color:#4A4A55;font-size:0.7rem;">{date}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:1.5rem 0;text-align:center;color:#6B6B7B;font-size:0.9rem;">
            还没有学习记录，快去开始学习吧
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ── 侧边栏 ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    # Profile
    st.markdown("""
    <div class="sidebar-profile">
        <div class="sp-icon">📈</div>
        <p class="sp-title">投资学院</p>
        <p class="sp-sub">Systematic Path to Alpha</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 导航
    nav_items = {
        "首页": "首页",
        "知识轨道": "知识轨道",
        "实践轨道": "实践轨道",
        "交易沙盒": "交易沙盒",
        "学习进度": "学习进度",
    }

    selected = st.radio(
        "导航",
        list(nav_items.keys()),
        label_visibility="collapsed",
        index=list(nav_items.keys()).index(st.session_state.page)
        if st.session_state.page in nav_items else 0,
    )
    st.session_state.page = selected

    st.markdown("<hr>", unsafe_allow_html=True)

    # 快捷统计
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
    <div class="sidebar-stats">
        <div class="ss-row">
            <span class="ss-label">已完成章节</span>
            <span class="ss-value">{done}</span>
        </div>
        <div class="ss-row">
            <span class="ss-label">测验均分</span>
            <span class="ss-value">{avg_q}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Git info
    try:
        import subprocess
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ACADEMY_ROOT,
            stderr=subprocess.DEVNULL,
            timeout=2
        ).decode().strip()
    except Exception:
        sha = "—"

    st.markdown(f"""
    <div style="padding:0 0.3rem;">
        <div class="ss-row">
            <span class="ss-label">版本</span>
            <span class="ss-value" style="font-size:0.7rem;color:#4A4A55;">{sha}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="sidebar-footer">Ctrl+C to stop</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ── Toast 欢迎 ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

if not st.session_state.welcome_shown:
    st.toast("欢迎回到投资学院，继续你的学习之旅")
    st.session_state.welcome_shown = True


# ══════════════════════════════════════════════════════════════
# ── 路由 ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

page = st.session_state.page

if page == "首页":
    render_home()
elif page == "知识轨道":
    render_knowledge_track()
elif page == "实践轨道":
    render_practice_track()
elif page == "交易沙盒":
    render_sandbox()
elif page == "学习进度":
    render_progress()
