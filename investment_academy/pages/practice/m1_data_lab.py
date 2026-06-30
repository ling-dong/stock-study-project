"""M1: 数据勘探实验室"""
import streamlit as st
import pandas as pd
from bridge.data_reader import list_available_etfs, load_etf_data, load_all_etf_metadata
from interactive.content_loader import load_lab_guide


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
        st.dataframe(meta, use_container_width=True, hide_index=True)
    else:
        st.warning("未找到 ETF 数据文件")

    # ETF 数据浏览器
    st.subheader("🔍 ETF 数据浏览器")
    etfs = list_available_etfs()
    if etfs:
        etf_codes = [e["code"] for e in etfs]
        selected_code = st.selectbox("选择 ETF", etf_codes)
        timeframe = st.selectbox("时间框架", ["day", "5min"])

        df = load_etf_data(selected_code, timeframe)
        if df is not None:
            st.metric("数据行数", len(df))
            st.dataframe(df.head(20), use_container_width=True)

            # 简易收盘价走势图
            if "close" in df.columns and "trade_date" in df.columns:
                st.subheader("收盘价走势")
                st.line_chart(
                    df.set_index("trade_date")["close"],
                    use_container_width=True,
                )
        else:
            st.warning(f"无法加载 {selected_code} 的 {timeframe} 数据")
    else:
        st.info("未找到可用的 ETF 数据")
