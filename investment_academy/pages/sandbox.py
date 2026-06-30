"""交易沙盒 — Streamlit 页面"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from bridge.data_reader import list_available_etfs, load_etf_data
from interactive.sandbox_engine import SandboxEngine


def show():
    st.markdown("## 🎮 交易沙盒")
    st.markdown("*用历史数据模拟真实交易决策，零风险积累经验*")

    # Initialize session state
    if "sandbox_engine" not in st.session_state:
        st.session_state.sandbox_engine = None
    if "sandbox_phase" not in st.session_state:
        st.session_state.sandbox_phase = "setup"  # setup | trading | done

    engine = st.session_state.sandbox_engine
    phase = st.session_state.sandbox_phase

    # ── Setup Phase ──
    if phase == "setup":
        _render_setup()

    # ── Trading Phase ──
    elif phase == "trading":
        _render_trading()

    # ── Results Phase ──
    elif phase == "done":
        _render_results()


def _render_setup():
    """设置阶段：选 ETF、时间段"""
    etfs = list_available_etfs()
    etf_codes = [e["code"] for e in etfs]

    col1, col2, col3 = st.columns(3)
    with col1:
        selected = st.selectbox("选择 ETF", etf_codes)
    with col2:
        initial_cash = st.number_input("初始资金", min_value=10000, value=100000, step=10000)

    # 加载数据预览
    if selected:
        df = load_etf_data(selected, "day")
        if df is not None:
            # 时间范围选择
            dates = df["trade_date"].unique()
            with col3:
                start_idx = st.selectbox("起始位置", range(len(dates) - 30),
                                         format_func=lambda i: str(dates[i])[:10])

            st.caption(f"共 {len(df)} 条数据 | 时间范围: {str(dates[0])[:10]} ~ {str(dates[-1])[:10]}")

            # 预览图
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["trade_date"], y=df["close"], mode="lines",
                                     name="收盘价", line=dict(color="#F0B90B", width=1)))
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
            st.plotly_chart(fig, use_container_width=True)

            if st.button("🚀 开始模拟交易", use_container_width=True):
                subset = df.iloc[start_idx:].reset_index(drop=True)
                st.session_state.sandbox_engine = SandboxEngine(subset, initial_cash)
                st.session_state.sandbox_phase = "trading"
                st.rerun()


def _render_trading():
    """交易阶段"""
    engine = st.session_state.sandbox_engine

    if engine is None or engine.is_done:
        st.session_state.sandbox_phase = "done"
        st.rerun()
        return

    bar = engine.current_bar

    # Top row: 日期 + 价格面板
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📅 日期", bar["date"])
    with col2:
        st.metric("💰 开盘", f"¥{bar['open']:.2f}")
    with col3:
        st.metric("📈 最高", f"¥{bar['high']:.2f}")
    with col4:
        st.metric("📉 最低", f"¥{bar['low']:.2f}")
    with col5:
        delta_color = "normal" if bar["close"] >= bar["open"] else "inverse"
        st.metric("🏁 收盘", f"¥{bar['close']:.2f}",
                  delta=f"{((bar['close']/bar['open']-1)*100):.2f}%")

    # 进度条
    progress = (bar["index"] + 1) / engine.state.total_bars
    st.progress(progress, text=f"进度: {bar['index']+1}/{engine.state.total_bars}")

    # 图表 + 控制
    chart_col, ctrl_col = st.columns([3, 1])

    with chart_col:
        _render_trading_chart(engine)

    with ctrl_col:
        # 投资组合摘要
        portfolio_value = engine.get_portfolio_value()
        pnl = portfolio_value - 100000.0
        pnl_pct = pnl / 100000.0 * 100

        st.metric("💼 总资产", f"¥{portfolio_value:,.0f}",
                  delta=f"{pnl_pct:+.2f}%")
        st.metric("💵 现金", f"¥{engine.state.cash:,.0f}")
        st.metric("📦 持仓", f"{engine.state.shares}股")

        if engine.state.shares > 0:
            cost = engine.get_current_cost_basis()
            unrealized = engine.get_unrealized_pnl()
            unrealized_pct = engine.get_unrealized_pnl_pct()
            st.metric("📊 成本价", f"¥{cost:.2f}")
            st.metric("📊 未实现盈亏", f"¥{unrealized:,.0f}",
                      delta=f"{unrealized_pct:+.2f}%")

        st.markdown("---")

        # 交易控制
        st.subheader("🎯 交易决策")

        # 买入
        can_buy, buy_msg = engine.can_buy()
        max_shares = int(engine.state.cash / (bar["close"] * 1.001) / 100) * 100
        buy_shares = st.number_input("买入股数", min_value=100, max_value=max(max_shares, 100),
                                     value=min(1000, max_shares), step=100,
                                     disabled=not can_buy)
        buy_reason = st.text_input("买入理由", key="buy_reason", placeholder="如：突破均线、放量上涨...")
        if st.button("🟢 买入", use_container_width=True, disabled=not can_buy):
            trade = engine.buy(int(buy_shares), buy_reason)
            if trade:
                st.toast(f"买入 {trade.shares} 股 @ ¥{trade.price:.2f}")
                st.rerun()
            else:
                st.error(buy_msg)

        st.markdown("---")

        # 卖出
        can_sell, sell_msg = engine.can_sell()
        sell_reason = st.text_input("卖出理由", key="sell_reason", placeholder="如：达到目标价、止损...")
        if st.button("🔴 全部卖出", use_container_width=True, disabled=not can_sell):
            trade = engine.sell(engine.state.shares, sell_reason)
            if trade:
                st.toast(f"卖出 {trade.shares} 股 @ ¥{trade.price:.2f}")
                st.rerun()

        st.markdown("---")

        # 跳过
        if st.button("⏭️ 跳过", use_container_width=True):
            engine.advance()
            st.rerun()

        # 结束
        if st.button("⏹️ 结束模拟", use_container_width=True):
            st.session_state.sandbox_phase = "done"
            st.rerun()

    # 交易记录
    if engine.state.trades:
        st.markdown("---")
        st.subheader("📋 交易记录")
        trade_data = []
        for t in engine.state.trades:
            trade_data.append({
                "日期": t.date,
                "操作": "买入" if t.action == "buy" else "卖出",
                "价格": f"¥{t.price:.2f}",
                "数量": f"{t.shares}股",
                "金额": f"¥{t.amount:,.0f}",
                "费用": f"¥{t.cost:.2f}",
                "理由": t.reason,
            })
        st.dataframe(pd.DataFrame(trade_data), use_container_width=True, hide_index=True)


def _render_trading_chart(engine):
    """渲染交易图表"""
    # 获取历史数据 + 当前点
    df = engine.df.iloc[:engine.state.current_index + 1].copy()

    fig = go.Figure()

    # K 线（简化版用线图）
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["close"], mode="lines",
        name="收盘价", line=dict(color="#F0B90B", width=1.5),
    ))

    # 当前价格标注
    if not engine.is_done:
        bar = engine.current_bar
        color = "#00FF00" if engine.state.shares > 0 else "#F0B90B"
        fig.add_trace(go.Scatter(
            x=[bar["date"]], y=[bar["close"]], mode="markers",
            name="当前", marker=dict(color=color, size=12, symbol="diamond"),
        ))

    # 买卖标注
    for t in engine.state.trades:
        marker_color = "#00FF00" if t.action == "buy" else "#FF4444"
        marker_symbol = "triangle-up" if t.action == "buy" else "triangle-down"
        fig.add_trace(go.Scatter(
            x=[t.date], y=[t.price], mode="markers",
            name=f"{'买入' if t.action == 'buy' else '卖出'} @ ¥{t.price:.2f}",
            marker=dict(color=marker_color, size=10, symbol=marker_symbol),
        ))

    fig.update_layout(
        height=400, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#1A1A1D"),
        yaxis=dict(showgrid=True, gridcolor="#1A1A1D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_results():
    """结果阶段"""
    engine = st.session_state.sandbox_engine

    if engine is None:
        st.session_state.sandbox_phase = "setup"
        st.rerun()
        return

    perf = engine.get_performance()

    st.markdown("## 🏆 模拟交易结果")

    # 核心指标
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        color = "normal" if perf.total_return_pct >= 0 else "inverse"
        st.metric("总收益", f"{perf.total_return_pct:+.2f}%",
                  delta=f"¥{perf.total_value - perf.initial_cash:+,.0f}")
    with col2:
        st.metric("总资产", f"¥{perf.total_value:,.0f}")
    with col3:
        st.metric("交易次数", perf.total_trades)
    with col4:
        st.metric("胜率", f"{perf.win_rate:.1%}" if perf.total_trades > 0 else "N/A")
    with col5:
        st.metric("最大回撤", f"-{perf.max_drawdown_pct:.2f}%")

    # 权益曲线
    st.subheader("📈 权益曲线")
    curve = engine.get_equity_curve()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3], vertical_spacing=0.05)

    fig.add_trace(go.Scatter(x=curve["date"], y=curve["value"], mode="lines",
                             name="总资产", line=dict(color="#F0B90B", width=2)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=curve["date"], y=curve["price"], mode="lines",
                             name="价格", line=dict(color="#888888", width=1)),
                  row=2, col=1)

    fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=0),
                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                     xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1A1A1D"))
    fig.update_xaxes(showgrid=True, gridcolor="#1A1A1D", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # 交易详情
    if engine.state.trades:
        st.subheader("📋 交易详情")
        trade_data = []
        for t in engine.state.trades:
            trade_data.append({
                "日期": t.date,
                "操作": "🟢买入" if t.action == "buy" else "🔴卖出",
                "价格": f"¥{t.price:.2f}",
                "数量": t.shares,
                "金额": f"¥{t.amount:,.0f}",
                "费用": f"¥{t.cost:.2f}",
                "理由": t.reason,
            })
        st.dataframe(pd.DataFrame(trade_data), use_container_width=True, hide_index=True)

    # 重新开始
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 重新开始", use_container_width=True):
            st.session_state.sandbox_engine = None
            st.session_state.sandbox_phase = "setup"
            st.rerun()
    with col2:
        if st.button("🏠 返回首页", use_container_width=True):
            st.session_state.sandbox_engine = None
            st.session_state.sandbox_phase = "setup"
            st.switch_page("app.py")
