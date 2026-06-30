"""P1: 股市基础 — 知识轨道页面"""
import streamlit as st
from interactive.content_loader import load_chapter, load_quiz
from interactive.quiz_widget import render_quiz
from db.repository import save_chapter_progress, get_chapter_progress


P1_CHAPTERS = [
    {"file": "chapter_01_stock_concept.md", "title": "第一章：什么是股票？", "id": "p1_ch1"},
    {"file": "chapter_02_etf_basics.md", "title": "第二章：ETF 入门", "id": "p1_ch2"},
    {"file": "chapter_03_a_share_rules.md", "title": "第三章：A股交易规则", "id": "p1_ch3"},
    {"file": "chapter_04_kline_intro.md", "title": "第四章：K线图入门", "id": "p1_ch4"},
    {"file": "chapter_05_ohlcv.md", "title": "第五章：基本术语", "id": "p1_ch5"},
]


def show():
    st.markdown("## 📚 P1: 股市基础")
    st.markdown("*从零开始，理解股票市场的基本概念*")

    # 章节选择
    chapter_labels = [ch["title"] for ch in P1_CHAPTERS]
    if chapter_labels:
        selected = st.sidebar.radio(
            "P1 目录", chapter_labels, label_visibility="collapsed"
        )
        idx = chapter_labels.index(selected)
        ch = P1_CHAPTERS[idx]

        # 加载章节内容
        content = load_chapter("p1_basics", ch["file"])
        if content:
            st.markdown(content, unsafe_allow_html=False)
        else:
            st.warning(f"📝 {ch['title']} 内容正在编写中…")
            return

        # 显示已有进度
        progress = get_chapter_progress(ch["id"])
        if progress and progress.get("completed"):
            st.success(f"✅ 已完成 — 测验得分: {progress.get('quiz_score', 0):.0%}")

        # 测验（仅当 quiz.yaml 匹配当前章节时显示）
        quiz_data = load_quiz("p1_basics")
        if quiz_data and quiz_data.get("chapter") == ch["id"]:
            result = render_quiz(quiz_data["questions"], ch["id"])
            if result and result.passed:
                save_chapter_progress(
                    chapter_id=ch["id"],
                    completed=True,
                    quiz_score=result.score,
                    quiz_attempts=1,
                )
