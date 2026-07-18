"""M1: 数据勘探实验室"""
import streamlit as st
import pandas as pd
from core.bridge.data_reader import list_available_etfs, load_etf_data, load_all_etf_metadata, get_etf_display_name
from core.engine.content_loader import load_lab_guide
from streamlit_app.widgets.kline_chart import create_kline_chart


def show():
    st.markdown("## 🔬 M1: 数据勘探实验室")
    st.markdown("*探索真实的 ETF 市场数据*")

    # 加载实验指南
    guide = load_lab_guide("m1_data_lab")
    if guide:
        with st.expander("📖 实验指南", expanded=True):
            st.markdown(guide)

    # ETF 元数据总览
    st.subheader("📊 可用 ETF 数据总览")
    meta = load_all_etf_metadata()
    if not meta.empty:
        # 添加名称列
        meta["名称"] = meta["code"].apply(lambda c: get_etf_display_name(c).split("  ")[-1] if "  " in get_etf_display_name(c) else "")
        st.dataframe(meta, use_container_width=True, hide_index=True)
    else:
        st.warning("未找到 ETF 数据文件")

    # ETF 数据浏览器
    st.subheader("🔍 ETF 数据浏览器")
    etfs = list_available_etfs()
    if etfs:
        # 构建显示名选择器
        display_to_code = {}
        display_names = []
        for e in etfs:
            dname = get_etf_display_name(e["code"])
            display_to_code[dname] = e["code"]
            display_names.append(dname)

        col1, col2 = st.columns([2, 1])
        with col1:
            selected_display = st.selectbox("选择 ETF", display_names)
            selected_code = display_to_code[selected_display]
        with col2:
            timeframe = st.selectbox("时间框架", ["day", "5min"])

        df = load_etf_data(selected_code, timeframe)
        if df is not None:
            st.metric("数据行数", len(df))

            # 专业 K 线图
            st.subheader("📈 K线图（含 MA5/MA10/MA20）")
            chart_df = df.tail(180) if timeframe == "day" else df.tail(300)
            fig = create_kline_chart(chart_df, show_volume=True, height=450)
            st.plotly_chart(fig, use_container_width=True)

            # 数据表格
            with st.expander("📋 查看原始数据"):
                st.dataframe(df.tail(30), use_container_width=True)
        else:
            st.warning(f"无法加载 {selected_display} 的 {timeframe} 数据")
    else:
        st.info("未找到可用的 ETF 数据")
