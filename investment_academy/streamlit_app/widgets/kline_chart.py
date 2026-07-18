"""专业 K 线图组件 — 蜡烛图 + 均线（同花顺风格）"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_kline_chart(
    df: pd.DataFrame,
    show_volume: bool = True,
    show_ma: list[int] = None,
    height: int = 500,
    title: str = "",
) -> go.Figure:
    """创建专业 K 线图

    Args:
        df: DataFrame with columns [trade_date, open, high, low, close, volume]
        show_volume: 是否显示成交量
        show_ma: 均线周期列表，默认 [5, 10, 20]
        height: 图表高度
        title: 图表标题

    Returns:
        Plotly Figure 对象
    """
    if show_ma is None:
        show_ma = [5, 10, 20]

    # 确保不修改原始 DataFrame
    df = df.copy()

    # 计算均线
    for period in show_ma:
        df[f"MA{period}"] = df["close"].rolling(window=period).mean()

    # 子图：K线 + 成交量
    if show_volume and "volume" in df.columns:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.7, 0.3], vertical_spacing=0.03,
        )
    else:
        fig = go.Figure()

    # ── K 线（蜡烛图） ──
    # A 股习惯：红涨绿跌
    candlestick = go.Candlestick(
        x=df["trade_date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="K线",
        increasing=dict(line=dict(color="#EF5350", width=1), fillcolor="#EF5350"),
        decreasing=dict(line=dict(color="#26A69A", width=1), fillcolor="#26A69A"),
        hovertext=[
            f"日期: {d}<br>开: {o:.3f}<br>高: {h:.3f}<br>低: {l:.3f}<br>收: {c:.3f}"
            for d, o, h, l, c in zip(
                df["trade_date"], df["open"], df["high"], df["low"], df["close"]
            )
        ],
        hoverinfo="text",
    )

    if show_volume and "volume" in df.columns:
        fig.add_trace(candlestick, row=1, col=1)
    else:
        fig.add_trace(candlestick)

    # ── 均线 ──
    ma_colors = {5: "#FFD54F", 10: "#FF8A65", 20: "#CE93D8", 60: "#64B5F6", 120: "#81C784"}
    for period in show_ma:
        col = f"MA{period}"
        if col not in df.columns:
            continue
        color = ma_colors.get(period, "#888888")
        ma_trace = go.Scatter(
            x=df["trade_date"],
            y=df[col],
            name=f"MA{period}",
            line=dict(color=color, width=1.2),
            mode="lines",
        )
        if show_volume and "volume" in df.columns:
            fig.add_trace(ma_trace, row=1, col=1)
        else:
            fig.add_trace(ma_trace)

    # ── 成交量 ──
    if show_volume and "volume" in df.columns:
        # 按涨跌上色
        colors = [
            "#EF5350" if close >= open_ else "#26A69A"
            for close, open_ in zip(df["close"], df["open"])
        ]
        vol_trace = go.Bar(
            x=df["trade_date"],
            y=df["volume"],
            name="成交量",
            marker=dict(color=colors, opacity=0.5),
            showlegend=False,
        )
        fig.add_trace(vol_trace, row=2, col=1)

    # ── 布局 ──
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(color="#F5F0E0", size=14)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#6B6B7B", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.12,
            xanchor="left",
            x=0,
            font=dict(color="#6B6B7B", size=10),
        ),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=40 if title else 20, b=10),
    )

    # X 轴
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#1A1A1D",
        zeroline=False,
        color="#6B6B7B",
    )
    if show_volume and "volume" in df.columns:
        fig.update_xaxes(row=2, col=1)

    # Y 轴
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1A1A1D",
        zeroline=False,
        color="#6B6B7B",
        title_text="价格",
    )
    if show_volume and "volume" in df.columns:
        fig.update_yaxes(
            row=1, col=1,
            showgrid=True, gridcolor="#1A1A1D",
            zeroline=False, color="#6B6B7B",
        )
        fig.update_yaxes(
            row=2, col=1,
            title_text="成交量",
            showgrid=False,
            zeroline=False,
            color="#6B6B7B",
        )

    return fig
