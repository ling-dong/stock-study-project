"""合成K线数据生成器 — 用于单元测试和回测验证"""
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import pandas as pd
from src.models.bar import BarOHLCV, TimeFrame, DataSource


def generate_bars(
    symbol: str = "510300.SH",
    timeframe: TimeFrame = TimeFrame.M5,
    n_bars: int = 200,
    start_price: float = 3.5,
    volatility: float = 0.01,
    trend: float = 0.0,
    seed: int = 42,
) -> list:
    """生成合成K线数据"""
    rng = np.random.default_rng(seed)
    returns = rng.normal(trend, volatility, n_bars)
    prices = start_price * np.exp(np.cumsum(returns))
    base_time = datetime(2026, 6, 24, 9, 30)
    bars = []
    for i in range(n_bars):
        p_open = float(prices[i])
        p_close = float(prices[i] * (1 + rng.normal(0, volatility * 0.5)))
        p_high = max(p_open, p_close) * (1 + abs(float(rng.normal(0, volatility * 0.3))))
        p_low = min(p_open, p_close) * (1 - abs(float(rng.normal(0, volatility * 0.3))))
        volume = int(abs(rng.normal(1_000_000, 300_000)))
        bar = BarOHLCV(
            symbol=symbol, timestamp=base_time + timedelta(minutes=5 * i),
            timeframe=timeframe,
            open=Decimal(str(round(p_open, 4))),
            high=Decimal(str(round(p_high, 4))),
            low=Decimal(str(round(p_low, 4))),
            close=Decimal(str(round(p_close, 4))),
            volume=volume,
            data_availability_time=base_time + timedelta(minutes=5 * i, seconds=1),
            source=DataSource.LOCAL,
        )
        bars.append(bar)
    return bars


def generate_trend_bars(symbol: str = "510300.SH", n_bars: int = 50,
                        direction: str = "up", seed: int = 42) -> list:
    """生成趋势K线序列(用于MarketStateSvc测试)"""
    trend_val = 0.002 if direction == "up" else -0.002
    return generate_bars(symbol=symbol, n_bars=n_bars, start_price=3.5,
                         volatility=0.005, trend=trend_val, seed=seed)


def generate_swing_bars(symbol: str = "510300.SH", n_bars: int = 100,
                        seed: int = 42) -> list:
    """生成震荡K线序列(包含两腿回撤结构)"""
    rng = np.random.default_rng(seed)
    prices = [3.5]
    for i in range(20):
        prices.append(prices[-1] * (1 + abs(float(rng.normal(0.003, 0.001)))))
    for i in range(10):
        prices.append(prices[-1] * (1 - abs(float(rng.normal(0.002, 0.001)))))
    for i in range(5):
        prices.append(prices[-1] * (1 + abs(float(rng.normal(0.001, 0.0005)))))
    for i in range(8):
        prices.append(prices[-1] * (1 - abs(float(rng.normal(0.0015, 0.0008)))))
    for i in range(10):
        prices.append(prices[-1] * (1 + abs(float(rng.normal(0.004, 0.002)))))
    base_time = datetime(2026, 6, 24, 9, 30)
    bars = []
    for i, price in enumerate(prices):
        bar = BarOHLCV(
            symbol=symbol, timestamp=base_time + timedelta(minutes=5 * i),
            timeframe=TimeFrame.M5,
            open=Decimal(str(round(price * 0.999, 4))),
            high=Decimal(str(round(price * 1.005, 4))),
            low=Decimal(str(round(price * 0.995, 4))),
            close=Decimal(str(round(price, 4))),
            volume=int(abs(rng.normal(1000000, 200000))),
            data_availability_time=base_time + timedelta(minutes=5 * i, seconds=1),
            source=DataSource.LOCAL,
        )
        bars.append(bar)
    return bars
