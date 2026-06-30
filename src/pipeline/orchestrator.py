"""事件驱动主流水线 — 串联全部模块 + 校准/事件总线/失效检测"""
from typing import Optional, List, Dict
from datetime import datetime
import logging
from src.models.bar import BarOHLCV
from src.models.prediction import PredictionOutput
from src.features.bar_feature import BarFeatureSvc
from src.features.market_state import MarketStateSvc
from src.features.setup_recog import SetupRecogSvc
from src.prediction.rule_engine import RuleEngine
from src.prediction.fusion import FusionLayer

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """SPAS主流水线 — 事件驱动，从K线闭合到信号产出的全链路

    可选集成 (V0.2):
    - CalibrationLayer: Isotonic Regression概率校准
    - EventStream: Redis Streams风格事件发布
    - FailureDetector: 六维模型失效检测
    """

    def __init__(
        self,
        calibration_layer=None,
        event_stream=None,
        failure_detector=None,
        ms_config: Optional[dict] = None,
        setup_config: Optional[dict] = None,
    ):
        self.bar_feature = BarFeatureSvc()
        self.market_state_svcs: Dict[str, MarketStateSvc] = {}
        self.setup_recog = SetupRecogSvc(**setup_config if setup_config else {})
        self.rule_engine = RuleEngine()
        self.fusion = FusionLayer()

        # 可选模块
        self.calibration = calibration_layer
        self.event_stream = event_stream
        self.failure_detector = failure_detector

        # 配置
        self._ms_config = ms_config or {}
        self._latest_signals: List[PredictionOutput] = []
        self._signal_count: int = 0

    def process_bar(self, bar: BarOHLCV) -> Optional[PredictionOutput]:
        """处理一根新闭合的K线

        完整链路:
        BarOHLCV → Features → MarketState → Setup → RuleEngine
        → [Calibration] → Prediction → [EventBus] → [FailureDetect]
        """
        # Step 1: 微观结构特征
        self.bar_feature.compute([bar])

        # Step 2: 市场状态机 (按symbol+timeframe维护独立实例)
        key = f"{bar.symbol}_{bar.timeframe.value}"
        if key not in self.market_state_svcs:
            self.market_state_svcs[key] = MarketStateSvc(**self._ms_config)
        market_state = self.market_state_svcs[key].update(bar)

        if market_state is None:
            return None

        # --- Event: 状态转移 ---
        self._publish("state_transition", {
            "symbol": bar.symbol, "timeframe": bar.timeframe.value,
            "new_state": market_state.state.value,
            "confidence": float(market_state.confidence),
        })

        # Step 3: Setup识别
        setup = self.setup_recog.update(bar)
        if setup is None:
            return None

        # --- Event: Setup检测 ---
        if not setup.is_confirmed:
            self._publish("setup_detected", {
                "symbol": bar.symbol, "setup_type": setup.setup_type.value,
                "status": "candidate", "quality": float(setup.quality_score),
            })
            return None

        self._publish("setup_detected", {
            "symbol": bar.symbol, "setup_type": setup.setup_type.value,
            "status": "confirmed", "quality": float(setup.quality_score),
        })

        # Step 4: 规则引擎
        current_price = float(bar.close)
        prediction = self.rule_engine.build_prediction(
            setup, market_state, current_price
        )

        # Step 5: 概率校准 (如果加载了校准器)
        if self.calibration is not None:
            raw = float(prediction.direction_prob)
            setup_type_str = setup.setup_type.value
            calibrated = self.calibration.calibrate(setup_type_str, raw)
            # 更新校准后的概率
            prediction = PredictionOutput(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                direction_prob=round(calibrated, 4),
                target_prob=round(calibrated * 0.7, 4),
                stop_prob=round((1.0 - calibrated) * 0.8, 4),
                r_r_ratio=prediction.r_r_ratio,
                expected_value=prediction.expected_value,
                setup_type=prediction.setup_type,
                model_version=prediction.model_version + "+calibrated",
                raw_probability=round(raw, 4),
                confidence_level=prediction.confidence_level,
            )

        # Step 6: 存储信号
        self._signal_count += 1
        self._latest_signals.append(prediction)
        if len(self._latest_signals) > 100:
            self._latest_signals = self._latest_signals[-100:]

        # --- Event: 预测产出 ---
        self._publish("prediction", {
            "symbol": bar.symbol,
            "setup_type": setup.setup_type.value,
            "direction_prob": float(prediction.direction_prob),
            "confidence": prediction.confidence_level,
        })

        # --- Failure Detector: 记录信号 ---
        if self.failure_detector is not None:
            self.failure_detector.record_trade(
                predicted_prob=float(prediction.direction_prob),
                actual_win=True,  # 待下次更新时修正
                trade_date=bar.timestamp.strftime("%Y-%m-%d") if bar.timestamp else "",
            )

        return prediction

    def _publish(self, stream: str, data: dict):
        """异步发布事件 (非阻塞, 静默失败)"""
        if self.event_stream is None:
            return
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.event_stream.publish(stream, data))
            except RuntimeError:
                pass  # 无事件循环, 跳过
        except Exception:
            pass  # 事件发布失败不影响主流程

    def get_latest_signal(self) -> Optional[PredictionOutput]:
        return self._latest_signals[-1] if self._latest_signals else None

    def get_signals(self, limit: int = 20) -> List[PredictionOutput]:
        return self._latest_signals[-limit:]

    def check_failure(self) -> Optional[dict]:
        """检查模型失效状态 (如果加载了FailureDetector)"""
        if self.failure_detector is None:
            return None
        return self.failure_detector.detect(
            current_drawdown=0.0,
            current_volatility=0.02,
            training_volatility=0.015,
            avg_correlation=0.5,
            bid_ask_spread=0.002,
            normal_spread=0.001,
        )

    def run_on_bars(self, bars: List[BarOHLCV]) -> List[PredictionOutput]:
        """批量处理K线序列"""
        predictions = []
        for bar in bars:
            pred = self.process_bar(bar)
            if pred is not None:
                predictions.append(pred)
        return predictions
