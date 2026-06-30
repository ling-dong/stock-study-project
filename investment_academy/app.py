"""投资学院 — Streamlit 主入口（Dark OLED Luxury · Claude Code 风格）"""
import sys
from pathlib import Path

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
#  全局 CSS — Dark OLED Luxury
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* === Base === */
    .stApp {
        background: #0A0A0B;
        background-image: radial-gradient(circle, #1A1A1D 1px, transparent 1px);
        background-size: 24px 24px;
    }
    .block-container { max-width: 1140px; padding-top: 1.2rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }

    #MainMenu, footer, .stDeployButton, div[data-testid="stToolbar"] { display: none !important; }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0A0A0B; }
    ::-webkit-scrollbar-thumb { background: #F0B90B33; border-radius: 4px; }

    /* === Typography === */
    h1, h2, h3 { color: #F5F0E0 !important; letter-spacing: 0.03em; font-weight: 300 !important; }
    h1 { font-size: 2rem !important; font-weight: 200 !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.1rem !important; font-weight: 400 !important; }
    p, li, div, span, label { color: #E8E6E3; }
    a { color: #F0B90B !important; text-decoration: none; }

    /* === Sidebar === */
    .stSidebar { background: #050506 !important; border-right: 1px solid #151518 !important; }
    .stSidebar [data-testid="stMarkdown"] h1 { font-size: 1.2rem !important; }
    .stSidebar .stRadio > div { gap: 0.15rem; }
    .stSidebar .stRadio label {
        padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.9rem;
        transition: background 0.2s;
    }
    .stSidebar .stRadio label:hover { background: #141417; }
    .stSidebar hr { border-color: #1A1A1D; margin: 0.75rem 0; }

    /* === Breadcrumb === */
    .breadcrumb { font-size: 0.78rem; color: #6B6B7B; margin-bottom: 1.2rem; letter-spacing: 0.05em; }
    .breadcrumb span { color: #F0B90B; }
    .breadcrumb a { color: #6B6B7B !important; }

    /* === Hero === */
    .hero { margin: 1.5rem 0 2.5rem; }
    .hero-eyebrow { font-size: 0.65rem; letter-spacing: 0.3em; color: #6B6B7B; margin-bottom: 0.5rem; }
    .hero-title { font-size: 2.8rem; font-weight: 200; color: #F5F0E0; margin-bottom: 0.3rem; line-height: 1.1; }
    .hero-sub { font-size: 0.95rem; color: #6B6B7B; }

    /* === Metric Cards === */
    .metrics-row { display: flex; gap: 1.2rem; margin: 1.5rem 0; }
    .m-card {
        flex: 1; background: #0D0D10; border: 1px solid #1A1A1D; border-radius: 10px;
        padding: 1.3rem; transition: border-color 0.3s, box-shadow 0.3s;
    }
    .m-card:hover { border-color: #F0B90B33; box-shadow: 0 0 20px #F0B90B08; }
    .m-value { font-size: 2rem; font-weight: 300; color: #F5F0E0; margin-bottom: 0.2rem; }
    .m-label { font-size: 0.75rem; color: #6B6B7B; letter-spacing: 0.08em; }
    .m-delta { font-size: 0.78rem; color: #F0B90B; margin-top: 0.3rem; }

    /* === Gold Divider === */
    .divider { height: 1px; background: linear-gradient(to right, #F0B90B44, transparent); margin: 2rem 0; }

    /* === Section Header === */
    .section-hd { margin-bottom: 1.2rem; }
    .section-hd h2 { font-size: 1.3rem !important; margin-bottom: 0.2rem !important; }
    .section-hd p { font-size: 0.82rem; color: #6B6B7B; }

    /* === Phase Cards Grid === */
    .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.9rem; }
    .p-card {
        background: #0D0D10; border: 1px solid #151518; border-radius: 10px;
        padding: 1.3rem; cursor: pointer; transition: all 0.25s;
    }
    .p-card:hover { border-color: #F0B90B44; box-shadow: 0 0 24px #F0B90B06; transform: translateY(-2px); }
    .p-card .p-num { font-size: 0.65rem; color: #F0B90B; letter-spacing: 0.15em; margin-bottom: 0.4rem; }
    .p-card .p-name { font-size: 1.05rem; font-weight: 400; color: #F5F0E0; margin-bottom: 0.3rem; }
    .p-card .p-desc { font-size: 0.78rem; color: #6B6B7B; margin-bottom: 0.8rem; line-height: 1.5; }
    .p-card .p-meta { display: flex; justify-content: space-between; align-items: center; }
    .p-card .p-count { font-size: 0.72rem; color: #4A4A55; }
    .p-card .p-badge { font-size: 0.68rem; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em; }
    .p-badge.done { background: #00FF8811; color: #00FF88; border: 1px solid #00FF8822; }
    .p-badge.progress { background: #F0B90B11; color: #F0B90B; border: 1px solid #F0B90B22; }
    .p-badge.wait { background: transparent; color: #4A4A55; border: 1px solid #1A1A1D; }

    /* === Progress Bar (mini, inside card) === */
    .mini-bar { height: 3px; background: #1A1A1D; border-radius: 2px; margin-top: 0.5rem; overflow: hidden; }
    .mini-bar-fill { height: 100%; background: linear-gradient(to right, #F0B90B88, #F0B90B); border-radius: 2px; }

    /* === Chapter List === */
    .ch-list { display: flex; flex-direction: column; gap: 0.4rem; }
    .ch-item {
        display: flex; align-items: center; gap: 0.8rem; padding: 0.7rem 0.9rem;
        background: #0D0D10; border: 1px solid #151518; border-radius: 8px;
        cursor: pointer; transition: all 0.2s;
    }
    .ch-item:hover { border-color: #F0B90B33; background: #0F0F14; }
    .ch-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .ch-dot.done { background: #00FF88; }
    .ch-dot.current { background: #F0B90B; box-shadow: 0 0 8px #F0B90B44; }
    .ch-dot.pending { background: #2A2A30; }
    .ch-title { flex: 1; font-size: 0.9rem; color: #E8E6E3; }
    .ch-score { font-size: 0.72rem; color: #6B6B7B; }

    /* === Back Button === */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: #0D0D10; border: 1px solid #252529; color: #F0B90B;
        font-size: 0.82rem; padding: 0.45rem 1.2rem; border-radius: 6px;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #F0B90B44; background: #F0B90B11;
    }

    /* === Buttons === */
    .btn-back {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.5rem 1.2rem; font-size: 0.82rem; color: #F0B90B;
        border: 1px solid #252529; border-radius: 6px; cursor: pointer; margin-bottom: 1.2rem;
        transition: all 0.2s; background: #0D0D10;
    }
    .btn-back:hover { color: #F0B90B; border-color: #F0B90B66; background: #141417; }

    /* === Continue Button === */
    .continue-wrap { margin: 0.8rem 0; }
    .continue-btn {
        display: inline-block; padding: 0.5rem 1.2rem; border: 1px solid #F0B90B44; border-radius: 20px;
        color: #F0B90B; font-size: 0.82rem; cursor: pointer; transition: all 0.3s; background: transparent;
    }
    .continue-btn:hover { background: #F0B90B11; border-color: #F0B90B; }

    /* === Activity Feed (Progress Page) === */
    .feed-item {
        display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 0;
        border-bottom: 1px solid #0F0F12; font-size: 0.82rem;
    }
    .feed-dot { width: 6px; height: 6px; border-radius: 50%; background: #F0B90B; flex-shrink: 0; }

    /* === Sandbox Inline Metrics === */
    .sandbox-bar { display: flex; gap: 0.8rem; margin: 0.8rem 0; }
    .sandbox-bar .stMetric { background: #0D0D10; border: 1px solid #151518; border-radius: 8px; padding: 0.6rem; }

    /* === Button inside cards === */
    .p-card + div .stButton { margin-top: -0.3rem; }
    .p-card + div .stButton button {
        background: transparent; border: 1px solid #252529; color: #F0B90B;
        font-size: 0.78rem; padding: 0.4rem 0; border-radius: 0 0 8px 8px;
        transition: all 0.2s;
    }
    .p-card + div .stButton button:hover {
        background: #F0B90B11; border-color: #F0B90B44; color: #F0B90B;
    }
    .p-card + div .stButton button:disabled {
        color: #3A3A40; border-color: #151518;
    }

    /* === Toast === */
    div[data-testid="stToast"] { background: #141417 !important; border: 1px solid #F0B90B44 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  导航状态机
# ══════════════════════════════════════════════════════════════

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "home"
if "kt_phase" not in st.session_state:
    st.session_state.kt_phase = None
if "kt_chapter" not in st.session_state:
    st.session_state.kt_chapter = None
if "pt_lab" not in st.session_state:
    st.session_state.pt_lab = None

# ══════════════════════════════════════════════════════════════
#  Sidebar — 顶级导航 + 快速统计 + 阶段进度
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;">
        <span style="font-size:1.4rem;">📈</span>
        <span style="font-size:1.05rem;font-weight:500;color:#F5F0E0;">投资学院</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 导航 ──
    nav_labels = {
        "home": "🏠  首页",
        "knowledge": "📚  知识轨道",
        "practice": "🔬  实践轨道",
        "sandbox": "🎮  交易沙盒",
        "progress": "📊  学习进度",
    }

    selected = st.radio(
        "导航",
        list(nav_labels.keys()),
        format_func=lambda k: nav_labels[k],
        key="nav_radio",
        index=list(nav_labels.keys()).index(st.session_state.nav_page),
        label_visibility="collapsed",
    )

    if selected != st.session_state.nav_page:
        st.session_state.nav_page = selected
        if selected != "knowledge":
            st.session_state.kt_phase = None
            st.session_state.kt_chapter = None
        if selected != "practice":
            st.session_state.pt_lab = None
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 统计数据 ──
    try:
        from db.repository import get_all_chapter_progress
        all_p = get_all_chapter_progress()
        done = sum(1 for p in all_p if p.get("completed"))
        scores = [p.get("quiz_score", 0) for p in all_p if p.get("completed") and p.get("quiz_score")]
        avg = sum(scores) / len(scores) * 100 if scores else 0
    except Exception:
        all_p = []
        done = 0
        avg = 0

    total_pct = done / 34 * 100
    st.markdown(f"""
    <div style="margin-bottom:0.8rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:0.2rem;">
            <span style="color:#6B6B7B;">总体进度</span>
            <span style="color:#F0B90B;">{done}/34</span>
        </div>
        <div style="height:4px;background:#1A1A1D;border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:{total_pct:.0f}%;background:linear-gradient(to right,#F0B90B88,#F0B90B);border-radius:2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if avg > 0:
        st.markdown(f'<div style="font-size:0.72rem;color:#6B6B7B;margin-bottom:0.3rem;">测验均分 <b style="color:#F0B90B;">{avg:.0f}%</b></div>',
                    unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 阶段进度迷你条 ──
    phase_names_short = [
        ("p1", "P1"),
        ("p2", "P2"),
        ("p3", "P3"),
        ("p4", "P4"),
        ("p5", "P5"),
        ("p6", "P6"),
        ("p7", "P7"),
    ]
    st.markdown('<div style="font-size:0.68rem;color:#4A4A55;letter-spacing:0.08em;margin-bottom:0.4rem;">阶段进度</div>',
                unsafe_allow_html=True)
    for pid, label in phase_names_short:
        prefix = pid + "_"
        chs = [p for p in all_p if p.get("chapter_id", "").startswith(prefix)]
        done_chs = sum(1 for p in chs if p.get("completed"))
        total_chs = max(len(chs), 1)
        pct = done_chs / total_chs * 100
        bar_color = "#00FF88" if pct >= 100 else ("#F0B90B" if pct > 0 else "#1A1A1D")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.25rem;">
            <span style="font-size:0.65rem;color:#6B6B7B;width:22px;">{label}</span>
            <div style="flex:1;height:3px;background:#1A1A1D;border-radius:2px;overflow:hidden;">
                <div style="height:100%;width:{pct:.0f}%;background:{bar_color};border-radius:2px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.6rem;color:#3A3A40;">Ctrl+C 停止</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════
#  渲染函数
# ══════════════════════════════════════════════════════════════

# ── 辅助组件 ────────────────────────────────────────────────

def _metrics_row(metrics: list[tuple]) -> str:
    """生成指标卡片行 HTML。每个 tuple: (value, label, delta?)"""
    cards = []
    for m in metrics:
        value, label = m[0], m[1]
        delta = m[2] if len(m) > 2 else ""
        d_html = f'<div class="m-delta">{delta}</div>' if delta else ""
        cards.append(f'<div class="m-card"><div class="m-value">{value}</div><div class="m-label">{label}</div>{d_html}</div>')
    return '<div class="metrics-row">' + "".join(cards) + "</div>"


def _breadcrumb(*parts):
    """面包屑 HTML"""
    items = []
    for i, p in enumerate(parts):
        if i == len(parts) - 1:
            items.append(f"<span>{p}</span>")
        else:
            items.append(f'<span style="color:#6B6B7B;">{p}</span>')
    return '<div class="breadcrumb">' + " / ".join(items) + "</div>"


def _badge(pct: float) -> str:
    if pct >= 100:
        return '<span class="p-badge done">已完成</span>'
    elif pct > 0:
        return '<span class="p-badge progress">进行中</span>'
    return '<span class="p-badge wait">未开始</span>'


def _mini_bar(pct: float) -> str:
    return f'<div class="mini-bar"><div class="mini-bar-fill" style="width:{min(pct,100):.0f}%;"></div></div>'


# ── 首页 ───────────────────────────────────────────────────

def _render_home():
    st.markdown("""
    <div class="hero">
        <p class="hero-eyebrow">INVESTMENT ACADEMY</p>
        <h1 class="hero-title">从零到投资大拿</h1>
        <p class="hero-sub">系统化掌握股市知识，用真实数据积累实战经验</p>
    </div>
    """, unsafe_allow_html=True)

    # 统计
    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception:
        all_progress = []

    completed = [p for p in all_progress if p.get("completed")]
    ch_done = len(completed)
    total_ch = 34
    score_vals = [p.get("quiz_score", 0) for p in completed if p.get("quiz_score", 0) > 0]
    avg_score = sum(score_vals) / len(score_vals) * 100 if score_vals else 0
    days = len(set((p.get("last_accessed") or "")[:10] for p in all_progress if p.get("last_accessed")))

    st.markdown(
        _metrics_row([
            (f"{ch_done} <span style='font-size:1rem;color:#6B6B7B;'>/ {total_ch}</span>",
             "已完成章节", f"完成率 {ch_done/max(total_ch,1)*100:.0f}%"),
            (f"{avg_score:.0f}<span style='font-size:1rem;color:#6B6B7B;'>%</span>" if avg_score > 0 else "—",
             "测验均分"),
            (str(max(days, 1)), "学习天数"),
        ]),
        unsafe_allow_html=True,
    )

    # 继续学习
    try:
        from db.repository import get_user_preferences
        phase_id = get_user_preferences().get("current_phase", "p1_basics")
    except Exception:
        phase_id = "p1_basics"

    phase_names = {
        "p1_basics": "P1 股市基础", "p2_technical": "P2 技术分析入门",
        "p3_sectors": "P3 板块与产业链", "p4_quant": "P4 量化策略思维",
        "p5_risk": "P5 风险管理", "p6_psychology": "P6 交易心理与市场情绪",
        "p7_integration": "P7 实战整合", "p1": "P1 股市基础",
    }

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("→ 继续学习", use_container_width=True, key="continue_btn"):
            st.session_state.nav_page = "knowledge"
            st.session_state.kt_phase = phase_id
            st.session_state.kt_chapter = None
            st.rerun()

    st.markdown(f'<p style="font-size:0.78rem;color:#6B6B7B;margin-top:0.3rem;">上次学到：{phase_names.get(phase_id, phase_id)}</p>',
                unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 学习路径
    st.markdown('<div class="section-hd"><h2>学习路径</h2><p>7 个阶段 · 34 章 · 从基础到系统</p></div>',
                unsafe_allow_html=True)

    path = [
        ("P1", "股市基础", "股票 / ETF / K线 / 交易规则", "5章", "p1"),
        ("P2", "技术分析", "趋势 / 微观结构 / 均线 / Wyckoff", "5章", "p2"),
        ("P3", "板块产业链", "行业分类 / 产业链 / 板块轮动", "4章", "p3"),
        ("P4", "量化策略", "概率思维 / 规则策略 / ML融合", "5章", "p4"),
        ("P5", "风险管理", "仓位 / 回撤 / 波动率 / 尾部风险", "5章", "p5"),
        ("P6", "交易心理", "情绪管理 / 认知偏差 / 市场情绪", "6章", "p6"),
        ("P7", "实战整合", "回测 / 偏差 / 完整交易系统", "4章", "p7"),
    ]

    # 计算各阶段完成度
    phase_pcts = {}
    for _, _, _, _, pid in path:
        chs = [p for p in all_progress if p.get("chapter_id", "").startswith(pid)]
        done_chs = [p for p in chs if p.get("completed")]
        phase_pcts[pid] = len(done_chs) / max(len(chs), 1) * 100 if chs else 0

    # 简化的学习路径时间线（纯展示，不可点击）
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for num, name, desc, count, pid in path:
        pct = phase_pcts.get(pid, 0)
        st.markdown(f"""
        <div class="p-card">
            <div class="p-num">{num}</div>
            <div class="p-name">{name}</div>
            <div class="p-desc">{desc}</div>
            <div class="p-meta">
                <span class="p-count">{count}</span>
                {_badge(pct)}
            </div>
            {_mini_bar(pct)}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 三个功能入口
    st.markdown('<div class="section-hd"><h2>功能</h2></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style="background:#0D0D10;border:1px solid #151518;border-radius:10px;padding:1.3rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">📚</div>
            <div style="font-weight:500;color:#F5F0E0;margin-bottom:0.3rem;">知识轨道</div>
            <div style="font-size:0.78rem;color:#6B6B7B;">34章系统课程</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入学习", key="feat_knowledge", use_container_width=True):
            st.session_state.nav_page = "knowledge"
            st.session_state.kt_phase = None
            st.session_state.kt_chapter = None
            st.rerun()
    with c2:
        st.markdown("""
        <div style="background:#0D0D10;border:1px solid #151518;border-radius:10px;padding:1.3rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">🔬</div>
            <div style="font-weight:500;color:#F5F0E0;margin-bottom:0.3rem;">实践轨道</div>
            <div style="font-size:0.78rem;color:#6B6B7B;">6个交互实验室</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入实验", key="feat_practice", use_container_width=True):
            st.session_state.nav_page = "practice"
            st.session_state.pt_lab = None
            st.rerun()
    with c3:
        st.markdown("""
        <div style="background:#0D0D10;border:1px solid #151518;border-radius:10px;padding:1.3rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">🎮</div>
            <div style="font-weight:500;color:#F5F0E0;margin-bottom:0.3rem;">交易沙盒</div>
            <div style="font-size:0.78rem;color:#6B6B7B;">零风险模拟交易</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("开始模拟", key="feat_sandbox", use_container_width=True):
            st.session_state.nav_page = "sandbox"
            st.rerun()


# ── 知识轨道 ──────────────────────────────────────────────

def _render_knowledge():
    phase = st.session_state.kt_phase
    chapter = st.session_state.kt_chapter

    # View: Reading
    if phase and chapter:
        _render_reading_view(phase, chapter)
        return

    # View: Chapter List
    if phase:
        _render_chapter_list(phase)
        return

    # View: Phase Grid (default)
    _render_phase_grid()


def _render_phase_grid():
    st.markdown(_breadcrumb("知识轨道"), unsafe_allow_html=True)
    st.markdown('<div class="section-hd"><h2>知识轨道</h2><p>选择学习阶段，开始系统化学习</p></div>',
                unsafe_allow_html=True)

    try:
        from db.repository import get_all_chapter_progress
        all_progress = get_all_chapter_progress()
    except Exception:
        all_progress = []

    phases = [
        ("p1_basics", "P1", "股市基础", "股票 / ETF / K线 / 交易规则", 5),
        ("p2_technical", "P2", "技术分析入门", "趋势 / 微观结构 / 均线 / Wyckoff", 5),
        ("p3_sectors", "P3", "板块与产业链", "行业分类 / 产业链 / 板块轮动", 4),
        ("p4_quant", "P4", "量化策略思维", "概率思维 / 规则策略 / ML融合", 5),
        ("p5_risk", "P5", "风险管理", "仓位 / 回撤 / 波动率 / 尾部风险", 5),
        ("p6_psychology", "P6", "交易心理与市场情绪", "情绪管理 / 认知偏差 / 市场情绪", 6),
        ("p7_integration", "P7", "实战整合", "回测 / 偏差 / 完整交易系统", 4),
    ]

    # Phase grid — st.columns 统一布局，卡片 + 按钮在同一列
    cols = st.columns(3)
    for i, (pid, num, name, desc, count) in enumerate(phases):
        prefix = pid[:2] + "_"
        chs = [p for p in all_progress if p.get("chapter_id", "").startswith(prefix)]
        done_chs = [p for p in chs if p.get("completed")]
        pct = len(done_chs) / max(len(chs), 1) * 100 if chs else 0

        with cols[i % 3]:
            # 卡片视觉
            st.markdown(f"""
            <div class="p-card">
                <div class="p-num">{num}</div>
                <div class="p-name">{name}</div>
                <div class="p-desc">{desc}</div>
                <div class="p-meta">
                    <span class="p-count">{count} 章</span>
                    {_badge(pct)}
                </div>
                {_mini_bar(pct)}
            </div>
            """, unsafe_allow_html=True)
            # 按钮与卡片紧贴
            if st.button("进入学习 →", key=f"phase_{pid}", use_container_width=True):
                st.session_state.kt_phase = pid
                st.session_state.kt_chapter = None
                st.rerun()


def _render_chapter_list(phase_id: str):
    from interactive.content_loader import load_chapter

    phase_names = {
        "p1_basics": "P1 股市基础",
        "p2_technical": "P2 技术分析入门",
        "p3_sectors": "P3 板块与产业链",
        "p4_quant": "P4 量化策略思维",
        "p5_risk": "P5 风险管理",
        "p6_psychology": "P6 交易心理与市场情绪",
        "p7_integration": "P7 实战整合",
    }
    phase_name = phase_names.get(phase_id, phase_id)

    st.markdown(_breadcrumb("知识轨道", phase_name), unsafe_allow_html=True)

    # Back button
    if st.button("← 返回阶段列表", key="back_to_phases"):
        st.session_state.kt_phase = None
        st.session_state.kt_chapter = None
        st.rerun()

    st.markdown(f'<div class="section-hd"><h2>{phase_name}</h2></div>', unsafe_allow_html=True)

    # Chapter definitions for P1 (extensible for P2-P7)
    all_chapters = {
        "p1_basics": [
            ("p1_ch1", "第一章", "什么是股票？", "chapter_01_stock_concept.md"),
            ("p1_ch2", "第二章", "ETF 入门", "chapter_02_etf_basics.md"),
            ("p1_ch3", "第三章", "A股交易规则", "chapter_03_a_share_rules.md"),
            ("p1_ch4", "第四章", "K线图入门", "chapter_04_kline_intro.md"),
            ("p1_ch5", "第五章", "基本术语", "chapter_05_ohlcv.md"),
        ],
    }

    chapters = all_chapters.get(phase_id, [])
    if not chapters:
        st.info("该阶段内容正在编写中…")
        return

    try:
        from db.repository import get_chapter_progress
    except Exception:
        get_chapter_progress = lambda x: None

    for ch_id, ch_num, ch_title, ch_file in chapters:
        prog = get_chapter_progress(ch_id) if get_chapter_progress else None
        is_done = prog and prog.get("completed")
        score = prog.get("quiz_score", 0) if prog else 0

        dot_cls = "done" if is_done else "pending"
        score_str = f'{score:.0%}' if is_done and score > 0 else ""

        # 单行布局：状态点 + 标题 + 分数 + 按钮
        c1, c2, c3, c4 = st.columns([0.05, 0.42, 0.18, 0.25])
        with c1:
            st.markdown(
                f'<div style="margin-top:0.65rem;"><div class="ch-dot {dot_cls}"></div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div style="padding:0.55rem 0;font-size:0.92rem;">{ch_num}：{ch_title}</div>'
                + (f'<div style="font-size:0.7rem;color:#00FF88;">得分 {score_str}</div>' if score_str else ""),
                unsafe_allow_html=True,
            )
        with c3:
            if is_done:
                st.markdown(
                    '<div style="margin-top:0.55rem;font-size:0.75rem;color:#00FF88;">✅ 已完成</div>',
                    unsafe_allow_html=True,
                )
        with c4:
            label = "重新学习" if is_done else "开始学习"
            if st.button(label, key=f"open_{ch_id}", use_container_width=True):
                st.session_state.kt_chapter = ch_id
                st.rerun()


def _render_reading_view(phase_id: str, chapter_id: str):
    from interactive.content_loader import load_chapter, load_quiz
    from interactive.quiz_widget import render_quiz
    from db.repository import save_chapter_progress, get_chapter_progress

    phase_names = {
        "p1_basics": "P1 股市基础",
    }
    chapter_names = {
        "p1_ch1": ("第一章", "什么是股票？", "chapter_01_stock_concept.md"),
        "p1_ch2": ("第二章", "ETF 入门", "chapter_02_etf_basics.md"),
        "p1_ch3": ("第三章", "A股交易规则", "chapter_03_a_share_rules.md"),
        "p1_ch4": ("第四章", "K线图入门", "chapter_04_kline_intro.md"),
        "p1_ch5": ("第五章", "基本术语", "chapter_05_ohlcv.md"),
    }

    phase_name = phase_names.get(phase_id, phase_id)
    ch_info = chapter_names.get(chapter_id, (chapter_id, "", ""))

    st.markdown(_breadcrumb("知识轨道", phase_name, f"{ch_info[0]}：{ch_info[1]}"),
                unsafe_allow_html=True)

    # Back button
    if st.button("← 返回章节列表", key="back_to_chapters"):
        st.session_state.kt_chapter = None
        st.rerun()

    # Load and render chapter content
    content = load_chapter(phase_id, ch_info[2])
    if content:
        st.markdown(content, unsafe_allow_html=False)
    else:
        st.warning(f"📝 {ch_info[0]}：{ch_info[1]} 内容正在编写中…")

    # Show existing progress
    prog = get_chapter_progress(chapter_id)
    if prog and prog.get("completed"):
        st.success(f"✅ 已完成 — 测验得分: {prog.get('quiz_score', 0):.0%}")

    # Quiz
    quiz_data = load_quiz(phase_id)
    if quiz_data:
        # Filter questions for this chapter
        chapter_questions = [q for q in quiz_data.get("questions", [])
                            if quiz_data.get("chapter") == chapter_id]
        if chapter_questions or quiz_data.get("chapter") == chapter_id:
            questions = chapter_questions or quiz_data.get("questions", [])
            result = render_quiz(questions, chapter_id)
            if result and result.passed:
                save_chapter_progress(
                    chapter_id=chapter_id,
                    completed=True,
                    quiz_score=result.score,
                    quiz_attempts=1,
                )
                st.rerun()


# ── 实践轨道 ──────────────────────────────────────────────

def _render_practice():
    lab = st.session_state.pt_lab

    if lab:
        _render_lab_view(lab)
        return

    _render_lab_grid()


def _render_lab_grid():
    st.markdown(_breadcrumb("实践轨道"), unsafe_allow_html=True)
    st.markdown('<div class="section-hd"><h2>实践轨道</h2><p>动手实验，用真实数据探索投资知识</p></div>',
                unsafe_allow_html=True)

    labs = [
        ("m1_data_lab", "M1", "数据勘探实验室", "浏览真实ETF数据，建立市场直觉", "已就绪"),
        ("m2_feature_lab", "M2", "特征工程实验室", "调节参数观察特征变化", "开发中"),
        ("m3_prediction", "M3", "预测引擎探索", "查看规则与ML预测对比", "开发中"),
        ("m4_risk_sandbox", "M4", "风控沙盒", "模拟仓位与止损场景", "开发中"),
        ("m5_backtest", "M5", "回测分析器", "解读回测指标与绩效", "开发中"),
        ("m6_sentiment", "M6", "市场情绪实验室", "情绪数据与行业分析", "开发中"),
    ]

    cols = st.columns(3)
    for i, (lid, num, name, desc, status) in enumerate(labs):
        badge_cls = "done" if status == "已就绪" else "wait"
        with cols[i % 3]:
            st.markdown(f"""
            <div class="p-card">
                <div class="p-num">{num}</div>
                <div class="p-name">{name}</div>
                <div class="p-desc">{desc}</div>
                <div class="p-meta">
                    <span class="p-count"></span>
                    <span class="p-badge {badge_cls}">{status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            disabled = status != "已就绪"
            label = "进入实验 →" if not disabled else "开发中…"
            if st.button(label, key=f"lab_{lid}", disabled=disabled, use_container_width=True):
                st.session_state.pt_lab = lid
                st.rerun()


def _render_lab_view(lab_id: str):
    lab_names = {
        "m1_data_lab": "M1 数据勘探实验室",
        "m2_feature_lab": "M2 特征工程实验室",
        "m3_prediction": "M3 预测引擎探索",
        "m4_risk_sandbox": "M4 风控沙盒",
        "m5_backtest": "M5 回测分析器",
        "m6_sentiment": "M6 市场情绪实验室",
    }
    lab_name = lab_names.get(lab_id, lab_id)

    st.markdown(_breadcrumb("实践轨道", lab_name), unsafe_allow_html=True)

    if st.button("← 返回实验室列表", key="back_to_labs"):
        st.session_state.pt_lab = None
        st.rerun()

    # 动态加载实验室页面
    module_name = f"pages.practice.{lab_id}"
    try:
        import importlib
        mod = importlib.import_module(module_name)
        if hasattr(mod, "show"):
            mod.show()
        else:
            st.info(f"🔬 {lab_name} 正在建设中…")
    except ImportError:
        st.info(f"🔬 {lab_name} 正在建设中…")
    except Exception as e:
        st.error(f"加载实验室失败: {e}")


# ── 交易沙盒 ──────────────────────────────────────────────

def _render_sandbox():
    st.markdown(_breadcrumb("交易沙盒"), unsafe_allow_html=True)

    try:
        from pages.sandbox import show as show_sandbox
        show_sandbox()
    except ImportError:
        st.info("🚧 交易沙盒正在建设中…")
    except Exception as e:
        st.error(f"加载交易沙盒失败: {e}")


# ── 学习进度 ──────────────────────────────────────────────

def _render_progress():
    st.markdown(_breadcrumb("学习进度"), unsafe_allow_html=True)
    st.markdown('<div class="section-hd"><h2>学习进度</h2><p>追踪你的学习旅程</p></div>',
                unsafe_allow_html=True)

    try:
        from db.repository import get_all_chapter_progress, get_quiz_results
        all_p = get_all_chapter_progress()
    except Exception as e:
        st.error(f"加载进度数据失败: {e}")
        return

    done = [p for p in all_p if p.get("completed")]
    total = 34
    pct = len(done) / total * 100

    st.markdown(_metrics_row([
        (str(len(done)), "已完成章节", f"{pct:.0f}%"),
        (str(len(all_p) - len(done)), "待完成"),
        (str(len(all_p)), "总互动章节"),
    ]), unsafe_allow_html=True)

    # 进度条
    st.progress(pct / 100, text=f"总体进度 {pct:.1f}%")

    # 最近完成的章节
    recent = sorted([p for p in done if p.get("last_accessed")],
                   key=lambda x: x.get("last_accessed", ""), reverse=True)[:5]
    if recent:
        st.markdown('<div style="margin-top:1.5rem;"><h3>最近完成</h3></div>', unsafe_allow_html=True)
        for r in recent:
            score = r.get("quiz_score", 0) * 100
            st.markdown(f"""
            <div class="feed-item">
                <div class="feed-dot"></div>
                <span style="flex:1;">{r['chapter_id']}</span>
                <span style="color:#F0B90B;font-size:0.78rem;">{score:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有完成任何章节，去知识轨道开始学习吧！")


# ══════════════════════════════════════════════════════════════
#  路由
# ══════════════════════════════════════════════════════════════

page = st.session_state.nav_page

if page == "home":
    _render_home()
elif page == "knowledge":
    _render_knowledge()
elif page == "practice":
    _render_practice()
elif page == "sandbox":
    _render_sandbox()
elif page == "progress":
    _render_progress()
else:
    _render_home()
