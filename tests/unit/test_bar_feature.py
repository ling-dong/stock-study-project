"""批次4: BarFeatureSvc单元测试 — K线微观结构6维特征"""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.features.bar_feature import BarFeatureSvc, EPSILON
from tests.fixtures.sample_data import generate_bars


class TestBarFeatureSvc:
    def setup_method(self):
        self.svc = BarFeatureSvc()

    def _make_bar(self, o, h, l, c, symbol="510300.SH", ts=None):
        if ts is None:
            ts = datetime(2026, 6, 24, 10, 0)
        return BarOHLCV(
            symbol=symbol, timestamp=ts, timeframe=TimeFrame.M5,
            open=Decimal(str(o)), high=Decimal(str(h)),
            low=Decimal(str(l)), close=Decimal(str(c)),
            volume=1000000,
            data_availability_time=ts + timedelta(seconds=1),
            source=DataSource.LOCAL,
        )

    def test_bull_bar_features(self):
        """阳线: close>open, body_ratio>0, trend_bar=1"""
        bar = self._make_bar(o=3.50, h=3.55, l=3.48, c=3.54)
        features = self.svc.compute([bar])

        fmap = {f.feature_name: f.feature_value for f in features}
        assert fmap["body_ratio"] > 0.3
        assert fmap["close_position"] > 0.7
        assert fmap["trend_bar"] == 1.0
        assert fmap["upper_shadow"] >= 0
        assert fmap["lower_shadow"] >= 0

    def test_bear_bar_features(self):
        """阴线: close<open, trend_bar=-1"""
        bar = self._make_bar(o=3.55, h=3.56, l=3.48, c=3.49)
        features = self.svc.compute([bar])
        fmap = {f.feature_name: f.feature_value for f in features}
        assert fmap["trend_bar"] == -1.0

    def test_doji_bar(self):
        """十字星: open≈close, body_ratio≈0"""
        bar = self._make_bar(o=3.50, h=3.55, l=3.45, c=3.50)
        features = self.svc.compute([bar])
        fmap = {f.feature_name: f.feature_value for f in features}
        assert fmap["body_ratio"] < 0.05  # nearly zero
        assert fmap["trend_bar"] == 0.0

    def test_feature_ranges(self):
        """所有[0,1]区间特征应在范围内"""
        bars = generate_bars(n_bars=50)
        features = self.svc.compute(bars)
        for fv in features:
            if fv.feature_name in ("body_ratio", "close_position", "upper_shadow", "lower_shadow"):
                assert 0.0 <= fv.feature_value <= 1.0, f"{fv.feature_name}={fv.feature_value}"

    def test_frozen_feature_vectors(self):
        """输出的FeatureVector应是frozen的"""
        bar = self._make_bar(o=3.50, h=3.55, l=3.48, c=3.54)
        features = self.svc.compute([bar])
        with pytest.raises(Exception):
            features[0].feature_value = 0.5  # frozen!

    def test_multiple_bars_output_count(self):
        """10根Bar应产生60个特征(10*6)"""
        bars = generate_bars(n_bars=10)
        features = self.svc.compute(bars)
        assert len(features) == 60

    def test_feature_computation_time(self):
        """每个特征应标注计算时间"""
        bar = self._make_bar(o=3.50, h=3.55, l=3.48, c=3.54)
        features = self.svc.compute([bar])
        for fv in features:
            assert fv.computation_time is not None
            assert fv.dependencies_version.startswith("bar_v")

    def test_single_high_low_bar(self):
        """单边市场: high=close=open or low=close=open 仍应能正常计算"""
        bar = self._make_bar(o=3.50, h=3.55, l=3.50, c=3.55)
        features = self.svc.compute([bar])
        fmap = {f.feature_name: f.feature_value for f in features}
        assert fmap["lower_shadow"] < EPSILON * 10  # nearly zero

    def test_limit_status_present(self):
        """涨跌停标记limit_status应存在且值∈{-1,0,1}"""
        bars = generate_bars(n_bars=20)
        features = self.svc.compute(bars)
        limit_features = [f for f in features if f.feature_name == "limit_status"]
        assert len(limit_features) == 20
        for lf in limit_features:
            assert lf.feature_value in (-1.0, 0.0, 1.0)
