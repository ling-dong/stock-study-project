"""批次1: 数据模型单元测试 — 覆盖全部8个Pydantic v2数据模型"""
from datetime import date, datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError

from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.models.feature import FeatureVector
from src.models.market_state import MarketState, MarketStateType
from src.models.setup_signal import SetupSignal, SetupType, SetupStatus
from src.models.prediction import PredictionOutput
from src.models.backtest import BacktestRecord
from src.models.sector_config import SectorConfig, ConstituentWeight
from src.models.version import SystemVersion


class TestBarOHLCV:
    def test_valid_bar(self):
        bar = BarOHLCV(
            symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.52"),
            low=Decimal("3.49"), close=Decimal("3.51"), volume=1000000,
            data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
            source=DataSource.LOCAL,
        )
        assert bar.symbol == "510300.SH"
        assert bar.timeframe == TimeFrame.M5

    def test_high_must_be_gte_max_open_close(self):
        with pytest.raises(ValidationError):
            BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                     timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.48"),
                     low=Decimal("3.49"), close=Decimal("3.51"), volume=1000000,
                     data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                     source=DataSource.LOCAL)

    def test_low_must_be_lte_min_open_close(self):
        with pytest.raises(ValidationError):
            BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                     timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.52"),
                     low=Decimal("3.51"), close=Decimal("3.49"), volume=1000000,
                     data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                     source=DataSource.LOCAL)

    def test_data_availability_time_must_be_gte_timestamp(self):
        with pytest.raises(ValidationError):
            BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                     timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.52"),
                     low=Decimal("3.49"), close=Decimal("3.51"), volume=1000000,
                     data_availability_time=datetime(2026, 6, 24, 9, 59),
                     source=DataSource.LOCAL)

    def test_volume_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                     timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.52"),
                     low=Decimal("3.49"), close=Decimal("3.51"), volume=-1,
                     data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                     source=DataSource.LOCAL)

    def test_stale_default_false(self):
        bar = BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                       timeframe=TimeFrame.M5, open=Decimal("3.5"), high=Decimal("3.52"),
                       low=Decimal("3.49"), close=Decimal("3.51"), volume=1000000,
                       data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                       source=DataSource.LOCAL)
        assert bar.stale is False
        assert bar.data_version == 1

    def test_all_timeframes(self):
        for tf in TimeFrame:
            bar = BarOHLCV(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                           timeframe=tf, open=Decimal("3.5"), high=Decimal("3.52"),
                           low=Decimal("3.49"), close=Decimal("3.51"), volume=1000000,
                           data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                           source=DataSource.LOCAL)
            assert bar.timeframe == tf


class TestFeatureVector:
    def test_frozen_model(self):
        fv = FeatureVector(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                           timeframe="5min", feature_name="body_ratio", feature_value=0.65,
                           computation_time=datetime(2026, 6, 24, 10, 0, 1),
                           dependencies_version="bar_v1")
        with pytest.raises(Exception):
            fv.feature_value = 0.8

    def test_future_function_violation_default(self):
        fv = FeatureVector(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                           timeframe="5min", feature_name="body_ratio", feature_value=0.65,
                           computation_time=datetime(2026, 6, 24, 10, 0, 1),
                           dependencies_version="bar_v1")
        assert fv.future_function_violation is False


class TestMarketState:
    def test_state_transitions(self):
        ms = MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                         timeframe="5min", state=MarketStateType.BULL,
                         confidence=Decimal("0.500"), duration=5)
        assert ms.is_trending is True
        assert ms.is_high_confidence is False

        ms_high = MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                              timeframe="5min", state=MarketStateType.BULL,
                              confidence=Decimal("0.750"), duration=15)
        assert ms_high.is_high_confidence is True

    def test_neutral_is_not_trending(self):
        ms = MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                         timeframe="5min", state=MarketStateType.NEUTRAL,
                         confidence=Decimal("0.800"), duration=10)
        assert ms.is_trending is False

    def test_bear_is_trending(self):
        ms = MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                         timeframe="5min", state=MarketStateType.BEAR,
                         confidence=Decimal("0.600"), duration=8)
        assert ms.is_trending is True

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                        timeframe="5min", state=MarketStateType.BULL,
                        confidence=Decimal("1.5"), duration=5)

    def test_duration_must_be_ge_1(self):
        with pytest.raises(ValidationError):
            MarketState(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                        timeframe="5min", state=MarketStateType.NEUTRAL,
                        confidence=Decimal("0.5"), duration=0)


class TestSetupSignal:
    def test_h2_candidate(self):
        s = SetupSignal(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                        setup_type=SetupType.H2, candidate_vs_confirmed=SetupStatus.CANDIDATE,
                        quality_score=Decimal("0.65"), maturity=0, detection_bar_index=100)
        assert s.is_confirmed is False

    def test_h2_confirmed_high_quality(self):
        s = SetupSignal(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 5),
                        setup_type=SetupType.H2, candidate_vs_confirmed=SetupStatus.CONFIRMED,
                        quality_score=Decimal("0.85"), maturity=3, detection_bar_index=103)
        assert s.is_confirmed is True
        assert s.is_high_quality is True

    def test_l2_and_fb_types(self):
        for st in [SetupType.L2, SetupType.FB]:
            s = SetupSignal(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                            setup_type=st, candidate_vs_confirmed=SetupStatus.CANDIDATE,
                            quality_score=Decimal("0.5"), maturity=0, detection_bar_index=1)
            assert s.setup_type == st

    def test_quality_score_bounds(self):
        with pytest.raises(ValidationError):
            SetupSignal(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                        setup_type=SetupType.H2, candidate_vs_confirmed=SetupStatus.CANDIDATE,
                        quality_score=Decimal("1.5"), maturity=0, detection_bar_index=1)


class TestPredictionOutput:
    def test_full_prediction(self):
        p = PredictionOutput(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                             direction_prob=Decimal("0.6500"), target_prob=Decimal("0.5500"),
                             stop_prob=Decimal("0.1500"), r_r_ratio=Decimal("2.500"),
                             expected_value=Decimal("0.008500"), setup_type="H2",
                             model_version="model_20260615_a1b2c3")
        assert float(p.direction_prob) == pytest.approx(0.65)

    def test_direction_prob_bounds(self):
        with pytest.raises(ValidationError):
            PredictionOutput(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                             direction_prob=Decimal("1.5"), target_prob=Decimal("0.5"),
                             stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.0"),
                             expected_value=Decimal("0.01"), setup_type="H2",
                             model_version="v1")

    def test_default_confidence_level(self):
        p = PredictionOutput(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                             direction_prob=Decimal("0.6500"), target_prob=Decimal("0.5500"),
                             stop_prob=Decimal("0.1500"), r_r_ratio=Decimal("2.500"),
                             expected_value=Decimal("0.008500"), setup_type="H2",
                             model_version="model_20260615_a1b2c3")
        assert p.confidence_level == "medium"
        assert p.raw_probability is None

    def test_negative_prob_rejected(self):
        with pytest.raises(ValidationError):
            PredictionOutput(symbol="510300.SH", timestamp=datetime(2026, 6, 24, 10, 0),
                             direction_prob=Decimal("-0.1"), target_prob=Decimal("0.5"),
                             stop_prob=Decimal("0.1"), r_r_ratio=Decimal("2.0"),
                             expected_value=Decimal("0.01"), setup_type="H2",
                             model_version="v1")


class TestBacktestRecord:
    def test_win_record(self):
        rec = BacktestRecord(version_id="System_v3.1", record_id=1, symbol="510300.SH",
                             entry_time=datetime(2026, 6, 24, 10, 0),
                             exit_time=datetime(2026, 6, 24, 11, 0),
                             entry_price=Decimal("3.5"), exit_price=Decimal("3.55"),
                             pnl=Decimal("0.05"), costs=Decimal("0.0025"),
                             setup_type="H2", position_size=Decimal("0.08"))
        assert rec.is_win is True
        assert float(rec.net_pnl) == pytest.approx(0.0475)

    def test_loss_record(self):
        rec = BacktestRecord(version_id="System_v3.1", record_id=2, symbol="510300.SH",
                             entry_time=datetime(2026, 6, 24, 10, 0),
                             exit_time=datetime(2026, 6, 24, 10, 30),
                             entry_price=Decimal("3.5"), exit_price=Decimal("3.45"),
                             pnl=Decimal("-0.05"), costs=Decimal("0.0025"),
                             setup_type="L2", position_size=Decimal("0.05"),
                             trigger_constraint="L1")
        assert rec.is_win is False
        assert float(rec.net_pnl) == pytest.approx(-0.0525)

    def test_open_position(self):
        rec = BacktestRecord(version_id="System_v3.1", record_id=3, symbol="510300.SH",
                             entry_time=datetime(2026, 6, 24, 10, 0),
                             entry_price=Decimal("3.5"), costs=Decimal("0.0025"),
                             setup_type="H2", position_size=Decimal("0.1"))
        assert rec.exit_time is None
        assert rec.pnl is None
        assert rec.net_pnl is None
        assert rec.is_win is None


class TestSectorConfig:
    def test_point_in_time_constituents(self):
        c1 = ConstituentWeight(code="002714.SZ", name="牧原股份", weight=Decimal("0.15"),
                               effective_from=date(2020, 1, 1), effective_to=date(2024, 12, 31))
        c2 = ConstituentWeight(code="002714.SZ", name="牧原股份", weight=Decimal("0.18"),
                               effective_from=date(2025, 1, 1), effective_to=None)
        sector = SectorConfig(sector_id="801010", name="农林牧渔", etf_code="159825.SZ",
                              index_code="801010.SI", constituents=[c1, c2])

        mid_2024 = date(2024, 6, 15)
        constituents = sector.get_constituents_at(mid_2024)
        assert len(constituents) == 1
        assert constituents[0].weight == Decimal("0.15")

        mid_2025 = date(2025, 6, 15)
        constituents = sector.get_constituents_at(mid_2025)
        assert constituents[0].weight == Decimal("0.18")

    def test_constituent_on_effective_to_date(self):
        c = ConstituentWeight(code="000001.SZ", name="平安银行", weight=Decimal("0.1"),
                              effective_from=date(2020, 1, 1), effective_to=date(2024, 12, 31))
        sector = SectorConfig(sector_id="801010", name="农林牧渔", etf_code="159825.SZ",
                              index_code="801010.SI", constituents=[c])
        assert len(sector.get_constituents_at(date(2024, 12, 31))) == 0
        assert len(sector.get_constituents_at(date(2024, 12, 30))) == 1

    def test_default_values(self):
        sector = SectorConfig(sector_id="801010", name="农林牧渔",
                              etf_code="159825.SZ", index_code="801010.SI")
        assert sector.timeframes == ["5min", "15min", "60min", "day"]
        assert sector.analysis_level == "basic"


class TestSystemVersion:
    def test_full_identifier(self):
        sv = SystemVersion(version_id="System_v3.1", rules_version="v2.3",
                           model_version="20240115_a1b2c3", features_version="v1.5",
                           data_version="2024q1")
        ident = sv.full_identifier
        assert "System_v3.1" in ident
        assert "rules_v2.3" in ident
        assert "model_20240115_a1b2c3" in ident
        assert "features_v1.5" in ident
        assert "data_2024q1" in ident

    def test_default_values(self):
        sv = SystemVersion(version_id="System_v3.1", rules_version="v2.3",
                           model_version="20240115_a1b2c3", features_version="v1.5",
                           data_version="2024q1")
        assert sv.calibration_params == {}
        assert sv.is_active is False

    def test_full_identifier_format(self):
        sv = SystemVersion(version_id="System_v1.0", rules_version="v1",
                           model_version="v1", features_version="v1", data_version="v1")
        expected = "System_v1.0={rules_v1,model_v1,features_v1,data_v1}"
        assert sv.full_identifier == expected
