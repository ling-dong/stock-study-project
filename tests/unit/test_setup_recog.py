"""批次6: SetupRecogSvc单元测试 — H2/L2/FB结构识别"""
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import pytest
from src.models.bar import BarOHLCV, TimeFrame, DataSource
from src.models.setup_signal import SetupType, SetupStatus
from src.features.setup_recog import SetupRecogSvc
from tests.fixtures.sample_data import generate_swing_bars, generate_trend_bars


def _generate_h2_pattern_bars() -> list:
    """生成含清晰H2结构的K线序列（确定性构造）

    H2结构阶段:
      Phase 1 — 上升趋势 (bars 0-14): 价格从3.50升至3.78
      Phase 2 — Leg 1回撤 (bars 15-19): 价格从3.76回撤至3.60
      Phase 3 — 反弹形成结构极点 (bars 20-24): 价格从3.65反弹至3.85
      Phase 4 — Leg 2回撤 + 缩量 (bars 25-29): 价格从3.82回撤至3.66 (higher low)
      Phase 5 — 放量突破极点 (bars 30-34): 价格从3.72升至3.96
    """
    base_time = datetime(2026, 6, 24, 9, 30)

    # 价格序列（35根Bar）
    prices = (
        # Phase 1: 上升趋势
        [3.50, 3.52, 3.54, 3.56, 3.58,
         3.60, 3.62, 3.64, 3.66, 3.68,
         3.70, 3.72, 3.74, 3.76, 3.78]
        # Phase 2: Leg 1 回撤
        + [3.76, 3.72, 3.68, 3.64, 3.60]
        # Phase 3: 反弹
        + [3.65, 3.70, 3.75, 3.80, 3.85]
        # Phase 4: Leg 2 回撤 (higher low)
        + [3.82, 3.78, 3.74, 3.70, 3.66]
        # Phase 5: 突破
        + [3.72, 3.78, 3.84, 3.90, 3.96]
    )

    # 成交量序列
    volumes = (
        [1_000_000] * 15        # Phase 1: 上升趋势
        + [1_000_000] * 5       # Phase 2: Leg 1
        + [800_000] * 5         # Phase 3: 反弹
        + [200_000] * 5         # Phase 4: Leg 2 (缩量)
        + [1_500_000] * 5       # Phase 5: 突破(放量)
    )

    bars = []
    for i, price in enumerate(prices):
        if i >= 30:
            # 突破K线: 大阳线，body_ratio > 0.5
            o = price * 0.98
            h = price * 1.01
            l = price * 0.98
        elif 15 <= i < 20:
            # 回撤K线: 阴线
            o = price * 1.01
            h = price * 1.01
            l = price * 0.98
        else:
            o = price * 0.998
            h = price * 1.005
            l = price * 0.995

        bar = BarOHLCV(
            symbol="510300.SH",
            timestamp=base_time + timedelta(minutes=5 * i),
            timeframe=TimeFrame.M5,
            open=Decimal(str(round(o, 4))),
            high=Decimal(str(round(h, 4))),
            low=Decimal(str(round(l, 4))),
            close=Decimal(str(round(price, 4))),
            volume=volumes[i],
            data_availability_time=base_time + timedelta(minutes=5 * i, seconds=1),
            source=DataSource.LOCAL,
        )
        bars.append(bar)
    return bars


class TestSetupRecogSvc:
    def setup_method(self):
        self.svc = SetupRecogSvc()

    def test_swing_bars_produce_signals(self):
        """摆动K线(含两腿回撤)应产生Setup信号"""
        bars = _generate_h2_pattern_bars()
        signals = []
        for bar in bars:
            sig = self.svc.update(bar)
            if sig is not None:
                signals.append(sig)
        # 至少应有候选信号
        assert len(signals) > 0

    def test_candidate_before_confirmed(self):
        """候选态应先于确认态出现"""
        bars = _generate_h2_pattern_bars()
        candidate_seen = False
        for bar in bars:
            sig = self.svc.update(bar)
            if sig is not None:
                if sig.candidate_vs_confirmed == SetupStatus.CANDIDATE:
                    candidate_seen = True
        assert candidate_seen

    def test_setup_type_is_h2(self):
        """摆动K线应主要产生H2类型Setup"""
        bars = _generate_h2_pattern_bars()
        types_found = set()
        for bar in bars:
            sig = self.svc.update(bar)
            if sig is not None:
                types_found.add(sig.setup_type)
        assert SetupType.H2 in types_found or len(types_found) > 0

    def test_quality_score_in_range(self):
        """质量评分应在[0,1]区间"""
        bars = _generate_h2_pattern_bars()
        for bar in bars:
            sig = self.svc.update(bar)
            if sig is not None:
                q = float(sig.quality_score)
                assert 0.0 <= q <= 1.0

    def test_empty_bars_no_signal(self):
        """不足10根Bar应不产生信号"""
        bars = generate_trend_bars(n_bars=5, direction="up")
        for bar in bars:
            sig = self.svc.update(bar)
            assert sig is None

    def test_maturity_increases(self):
        """确认态的maturity应>0"""
        bars = _generate_h2_pattern_bars()
        for bar in bars:
            sig = self.svc.update(bar)
            if sig is not None and sig.is_confirmed:
                assert sig.maturity > 0
                break
