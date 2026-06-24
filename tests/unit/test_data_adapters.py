"""批次3: 数据采集层单元测试"""
import asyncio
import pytest
import pandas as pd
from src.data.adapters.local import LocalAdapter
from src.data.fetcher import DataFetcher
from src.data.adjustment import PriceAdjuster
from src.data.quality import DataQualityMonitor
from tests.fixtures.sample_data import generate_bars


class TestLocalAdapter:
    @pytest.mark.asyncio
    async def test_save_and_load(self, tmp_path):
        adapter = LocalAdapter(data_dir=str(tmp_path))
        bars = generate_bars(n_bars=10)
        df = pd.DataFrame([{
            "timestamp": b.timestamp, "open": float(b.open), "high": float(b.high),
            "low": float(b.low), "close": float(b.close), "volume": b.volume, "factor": 1.0,
        } for b in bars])
        await adapter.save_bars("510300.SH", "5min", df)
        loaded = await adapter.get_bars("510300.SH", "5min")
        assert len(loaded) == 10

    @pytest.mark.asyncio
    async def test_empty_for_missing_file(self, tmp_path):
        adapter = LocalAdapter(data_dir=str(tmp_path))
        df = await adapter.get_bars("UNKNOWN.SH", "5min")
        assert df.empty

    @pytest.mark.asyncio
    async def test_health_check(self, tmp_path):
        adapter = LocalAdapter(data_dir=str(tmp_path))
        assert await adapter.health_check() is True


class TestDataFetcher:
    @pytest.mark.asyncio
    async def test_fallback_to_local(self, tmp_path):
        fetcher = DataFetcher.with_defaults(data_dir=str(tmp_path))
        adapter = LocalAdapter(data_dir=str(tmp_path))
        bars = generate_bars(n_bars=5)
        df = pd.DataFrame([{
            "timestamp": b.timestamp, "open": float(b.open), "high": float(b.high),
            "low": float(b.low), "close": float(b.close), "volume": b.volume, "factor": 1.0,
        } for b in bars])
        await adapter.save_bars("510300.SH", "5min", df)
        df = await fetcher.get_bars("510300.SH", "5min")
        assert len(df) == 5

    @pytest.mark.asyncio
    async def test_unknown_symbol_returns_empty(self):
        fetcher = DataFetcher.with_defaults()
        df = await fetcher.get_bars("NONEXIST.SH", "5min")
        assert df.empty


class TestPriceAdjuster:
    def test_basic_adjustment(self):
        from decimal import Decimal
        from datetime import date
        adjuster = PriceAdjuster()
        adjuster.set_daily_factors("510300.SH", {
            date(2026, 6, 24): Decimal("1.5"),
            date(2026, 6, 25): Decimal("1.0"),
        })
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 24))
        assert float(adj) == pytest.approx(100.0)
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 25))
        assert float(adj) == pytest.approx(100.0 * 1.0 / 1.5)

    def test_missing_factor_returns_nan(self):
        from decimal import Decimal
        from datetime import date
        adjuster = PriceAdjuster()
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 25))
        assert adj.is_nan()


class TestDataQualityMonitor:
    def test_completeness_pass(self):
        monitor = DataQualityMonitor()
        df = pd.DataFrame({"a": range(96)})
        ok, rate = monitor.check_completeness(df, expected_count=100)
        assert ok

    def test_completeness_fail(self):
        monitor = DataQualityMonitor()
        df = pd.DataFrame({"a": range(90)})
        ok, rate = monitor.check_completeness(df, expected_count=100)
        assert not ok

    def test_anomaly_detection(self):
        monitor = DataQualityMonitor(max_bar_change_pct=10.0)
        df = pd.DataFrame({
            "open": [100, 100, 100],
            "close": [102, 115, 98],
            "volume": [1000000, 1000000, 1000000],
        })
        anomalies = monitor.detect_anomalies(df, avg_volume_20d=1000000)
        assert anomalies.iloc[1]
        assert not anomalies.iloc[0]
