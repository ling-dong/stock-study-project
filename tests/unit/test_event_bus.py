"""批次2: 事件总线 + 配置加载单元测试"""
import asyncio
import pytest
from src.event_bus.stream import EventStream
from src.event_bus.events import (
    EventHeader, BarCloseEvent, FeatureComputeEvent,
    StateTransitionEvent, SetupDetectedEvent,
)
from src.config.loader import load_config, AppConfig


class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = EventStream()
        await bus.publish("test", {"msg": "hello"})
        async for eid, event in bus.subscribe("test", block_ms=100):
            assert event == {"msg": "hello"}
            break

    @pytest.mark.asyncio
    async def test_multiple_streams(self):
        bus = EventStream()
        await bus.publish("stream_a", {"data": "a"})
        await bus.publish("stream_b", {"data": "b"})
        results = {}
        async for eid, event in bus.subscribe("stream_a", block_ms=100):
            results["a"] = event; break
        async for eid, event in bus.subscribe("stream_b", block_ms=100):
            results["b"] = event; break
        assert results["a"] == {"data": "a"}
        assert results["b"] == {"data": "b"}

    @pytest.mark.asyncio
    async def test_bar_close_event(self):
        bus = EventStream()
        header = EventHeader(source_service="data_fetcher")
        bar_event = BarCloseEvent(
            header=header, symbol="510300.SH", timeframe="5min",
            bar_timestamp="2026-06-24T10:00:00",
            data_availability_time="2026-06-24T10:00:01",
            open=3.5, high=3.52, low=3.49, close=3.51, volume=1000000,
        )
        await bus.publish("stream:bar_close", bar_event)
        async for eid, event in bus.subscribe("stream:bar_close", block_ms=100):
            assert isinstance(event, BarCloseEvent)
            assert event.symbol == "510300.SH"
            assert event.close == 3.51
            break

    @pytest.mark.asyncio
    async def test_consumer_group_isolation(self):
        bus = EventStream()
        await bus.publish("multi", {"msg": 1})
        await bus.publish("multi", {"msg": 2})
        group_a = []
        async for eid, event in bus.subscribe("multi", group="group_a", block_ms=100):
            group_a.append(event)
            if len(group_a) >= 2: break
        group_b = []
        async for eid, event in bus.subscribe("multi", group="group_b", block_ms=100):
            group_b.append(event)
            if len(group_b) >= 2: break
        assert len(group_a) == 2
        assert len(group_b) == 2

    @pytest.mark.asyncio
    async def test_stream_length(self):
        bus = EventStream()
        assert await bus.stream_length("empty") == 0
        await bus.publish("test", {"msg": 1})
        assert await bus.stream_length("test") == 1

    @pytest.mark.asyncio
    async def test_reset(self):
        bus = EventStream()
        await bus.publish("test", {"msg": 1})
        await bus.reset()
        assert await bus.stream_length("test") == 0


class TestConfigLoader:
    def test_default_config(self):
        config = AppConfig()
        assert config.risk_constraints.L1_daily_stop == -0.03
        assert config.kelly.fraction == 0.25
        assert config.market_state.adx_threshold == 20  # 日线校准
        assert config.calibration.ece_threshold == 0.01

    def test_load_from_yaml(self):
        config = load_config("config")
        assert isinstance(config, AppConfig)
        assert config.market_state.confirmation_bars == 2

    def test_trading_costs(self):
        config = AppConfig()
        assert config.trading_costs.commission_bps == 0.25
        assert config.trading_costs.stamp_duty_bps == 1.0

    def test_setup_weights_sum(self):
        config = AppConfig()
        w = config.setup.quality_weights
        total = w["pullback_similarity"] + w["volume_shrink"] + w["breakout_momentum"]
        assert abs(total - 1.0) < 0.01

    def test_all_sections(self):
        config = AppConfig()
        assert config.risk_constraints is not None
        assert config.volatility_anchor is not None
        assert config.backtest is not None
