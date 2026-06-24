"""事件驱动主流水线 — 串联全部模块"""
from typing import Optional, List, Dict
from datetime import datetime
from src.models.bar import BarOHLCV
from src.models.prediction import PredictionOutput
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.prediction.fusion import FusionLayer


class PipelineOrchestrator:
    """SPAS主流水线 — 事件驱动，从K线闭合到信号产出的全链路"""

    def __init__(self):
        self.bar_feature = BarFeatureSvc()
        self.market_state_svcs: Dict[str, MarketStateSvc] = {}
        self.setup_recog = SetupRecogSvc()
        self.rule_engine = RuleEngine()
        self.fusion = FusionLayer()
        self._latest_signals: List[PredictionOutput] = []

    def process_bar(self, bar: BarOHLCV) -> Optional[PredictionOutput]:
        """处理一根新闭合的K线

        完整链路: BarOHLCV -> Features -> MarketState -> Setup -> RuleEngine -> Prediction
        """
        # Step 1: 微观结构特征
        features = self.bar_feature.compute([bar])

        # Step 2: 市场状态机(按symbol+timeframe维护独立实例)
        key = f"{bar.symbol}_{bar.timeframe.value}"
        if key not in self.market_state_svcs:
            self.market_state_svcs[key] = MarketStateSvc()
        market_state = self.market_state_svcs[key].update(bar)

        if market_state is None:
            return None

        # Step 3: Setup识别
        setup = self.setup_recog.update(bar)
        if setup is None or not setup.is_confirmed:
            return None

        # Step 4: 规则引擎
        current_price = float(bar.close)
        prediction = self.rule_engine.build_prediction(setup, market_state, current_price)

        # Step 5: 存储最新信号
        self._latest_signals.append(prediction)
        if len(self._latest_signals) > 100:
            self._latest_signals = self._latest_signals[-100:]

        return prediction

    def get_latest_signal(self) -> Optional[PredictionOutput]:
        return self._latest_signals[-1] if self._latest_signals else None

    def get_signals(self, limit: int = 20) -> List[PredictionOutput]:
        return self._latest_signals[-limit:]

    def run_on_bars(self, bars: List[BarOHLCV]) -> List[PredictionOutput]:
        """批量处理K线序列"""
        predictions = []
        for bar in bars:
            pred = self.process_bar(bar)
            if pred is not None:
                predictions.append(pred)
        return predictions
