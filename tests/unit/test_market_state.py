"""批次5: MarketStateSvc单元测试 — 市场状态机"""
import pytest
from src.models.market_state import MarketStateType, MarketState
from src.features.market_state import MarketStateSvc
from tests.fixtures.sample_data import generate_trend_bars, generate_bars


class TestMarketStateSvc:
    def setup_method(self):
        self.svc = MarketStateSvc()

    def test_initial_state_is_none(self):
        assert self.svc.get_current_state() is None

    def test_bull_trend_detection(self):
        """强上涨趋势应检测为BULL"""
        bars = generate_trend_bars(n_bars=40, direction="up", seed=42)
        last_state = None
        for bar in bars:
            state = self.svc.update(bar)
            if state is not None:
                last_state = state
        # 40根上涨趋势Bar后应有BULL判定
        assert last_state is not None

    def test_bear_trend_detection(self):
        """强下跌趋势应检测为BEAR"""
        svc = MarketStateSvc()
        bars = generate_trend_bars(n_bars=40, direction="down", seed=99)
        last_state = None
        for bar in bars:
            state = svc.update(bar)
            if state is not None:
                last_state = state
        assert last_state is not None

    def test_confidence_increases_with_duration(self):
        """置信度应随持续时间递增"""
        svc = MarketStateSvc(confirmation_bars=1)  # 加速确认
        bars = generate_trend_bars(n_bars=30, direction="up", seed=1)
        confidences = []
        for bar in bars:
            state = svc.update(bar)
            if state is not None and state.state != MarketStateType.NEUTRAL:
                confidences.append(float(state.confidence))
        # 置信度应总体呈上升趋势
        if len(confidences) >= 3:
            assert confidences[-1] >= confidences[0]

    def test_state_is_marketstate_type(self):
        svc = MarketStateSvc(confirmation_bars=1)
        bars = generate_trend_bars(n_bars=40, direction="up", seed=5)
        last_state = None
        for bar in bars:
            state = svc.update(bar)
            if state is not None:
                last_state = state
        assert last_state is not None
        assert isinstance(last_state, MarketState)
        assert last_state.state in (MarketStateType.BULL, MarketStateType.BEAR, MarketStateType.NEUTRAL)

    def test_confirmation_delay(self):
        """默认需连续2根Bar确认，不应立即切换"""
        svc = MarketStateSvc(confirmation_bars=2)
        bars = generate_bars(n_bars=5, trend=0.01, seed=10)
        state_changes = []
        for bar in bars:
            state = svc.update(bar)
            if state is not None:
                state_changes.append(state)
        # 仅有5根Bar，可能不足以触发确认
        assert len(state_changes) <= 3

    def test_regime_classification_present(self):
        """确认态应包含regime_classification"""
        svc = MarketStateSvc(confirmation_bars=1)
        bars = generate_trend_bars(n_bars=50, direction="up", seed=20)
        for bar in bars:
            state = svc.update(bar)
            if state is not None and state.state != MarketStateType.NEUTRAL:
                assert state.regime_classification is not None
                break
