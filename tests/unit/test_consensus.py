"""批次7: ConsensusSvc单元测试 — 板块一致性"""
from datetime import datetime, timedelta
import pytest
from src.features.consensus import ConsensusSvc
from tests.fixtures.sample_data import generate_bars


class TestConsensusSvc:
    def setup_method(self):
        self.svc = ConsensusSvc()

    def test_basic_consensus(self):
        """基本板块一致性计算"""
        leader1 = generate_bars(symbol="000001.SZ", n_bars=20, trend=0.005, seed=1)
        leader2 = generate_bars(symbol="000002.SZ", n_bars=20, trend=0.003, seed=2)
        constituents = [("000001.SZ", leader1), ("000002.SZ", leader2)]
        ref_time = max(b[-1].data_availability_time for _, b in constituents)

        features, is_stale = self.svc.compute("801010", constituents, ref_time)
        assert not is_stale
        fmap = {f.feature_name: f.feature_value for f in features}
        assert "up_ratio" in fmap
        assert "momentum_median" in fmap
        assert "leader_corr" in fmap
        assert 0.0 <= fmap["up_ratio"] <= 1.0

    def test_stale_detection(self):
        """过期数据应触发stale标记"""
        old_bars = generate_bars(n_bars=20, seed=1)
        constituents = [("000001.SZ", old_bars)]
        old_time = datetime.now() - timedelta(seconds=10)  # > 5s stale threshold
        features, is_stale = self.svc.compute("801010", constituents, old_time)
        assert is_stale

    def test_single_constituent(self):
        """单一成分股(无龙头相关性)"""
        bars = generate_bars(symbol="000001.SZ", n_bars=20, seed=1)
        ref_time = bars[-1].data_availability_time
        features, is_stale = self.svc.compute("801010", [("000001.SZ", bars)], ref_time)
        fmap = {f.feature_name: f.feature_value for f in features}
        assert "up_ratio" in fmap
        assert "leader_corr" in fmap
        assert fmap["leader_corr"] == 0.0

    def test_up_ratio_range(self):
        """up_ratio应在[0,1]区间"""
        up_bars = generate_bars(n_bars=20, trend=0.01, seed=10)
        down_bars = generate_bars(n_bars=20, trend=-0.01, seed=20)
        constituents = [("up", up_bars), ("down", down_bars)]
        ref_time = max(b[-1].data_availability_time for _, b in constituents)
        features, _ = self.svc.compute("801010", constituents, ref_time)
        fmap = {f.feature_name: f.feature_value for f in features}
        assert 0.0 <= fmap["up_ratio"] <= 1.0
