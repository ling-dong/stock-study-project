# SPAS 股市板块涨跌概率分析系统 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零构建SPAS全量生产系统——模块化单体Python架构，覆盖数据采集、特征工程、预测模型、风控、回测全部模块

**Architecture:** Python 3.11+ 模块化单体，内部事件总线（Redis Streams语义），4特征模块+3层预测+6层风控+Walk-Forward回测

**Tech Stack:** Python 3.11+, pandas, numpy, Pydantic v2, asyncio, LightGBM, scikit-learn, pytest, FastAPI, YAML

**设计文档基准:** `sector_probability_system.agent.final.md` V1.0（2026-06-23修订版）

---

## 文件结构

```
stock_market/
├── config/
│   ├── settings.yaml
│   └── sectors.yaml
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── bar.py              # BarOHLCV, BarAdjustment
│   │   ├── feature.py          # FeatureVector
│   │   ├── market_state.py     # MarketState
│   │   ├── setup_signal.py     # SetupSignal
│   │   ├── prediction.py       # PredictionOutput
│   │   ├── backtest.py         # BacktestRecord
│   │   ├── sector_config.py    # SectorConfig
│   │   └── version.py          # SystemVersion
│   ├── event_bus/
│   │   ├── __init__.py
│   │   ├── events.py           # 事件类型定义
│   │   └── stream.py           # Redis Streams语义实现
│   ├── config/
│   │   ├── __init__.py
│   │   └── loader.py           # YAML配置加载+Pydantic校验
│   ├── data/
│   │   ├── __init__.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # UDAI统一接口
│   │   │   ├── tushare.py      # Tushare Pro适配器
│   │   │   ├── akshare.py      # AKShare适配器
│   │   │   └── local.py        # 本地Parquet缓存
│   │   ├── fetcher.py          # 多源协调+健康状态机
│   │   ├── adjustment.py       # 分钟级复权因子
│   │   └── quality.py          # 数据质量监控
│   ├── features/
│   │   ├── __init__.py
│   │   ├── bar_feature.py      # BarFeatureSvc
│   │   ├── market_state.py     # MarketStateSvc
│   │   ├── setup_recog.py      # SetupRecogSvc
│   │   └── consensus.py        # ConsensusSvc
│   ├── prediction/
│   │   ├── __init__.py
│   │   ├── rule_engine.py      # Layer 1 规则引擎
│   │   ├── ml_model.py         # Layer 2 LightGBM+Transformer
│   │   ├── calibration.py      # Layer 3 Isotonic Regression
│   │   └── fusion.py           # 融合+MTF投票
│   ├── sentiment/
│   │   ├── __init__.py
│   │   ├── collector.py
│   │   ├── nlp.py
│   │   └── cache.py
│   ├── sector_linkage/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── exhaustion.py
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── constraints.py      # 六层硬约束
│   │   ├── kelly.py            # 凯利公式
│   │   ├── volatility.py       # 波动率锚定
│   │   ├── tail_risk.py        # 黑天鹅+熔断
│   │   ├── liquidity.py        # 流动性监控
│   │   └── failure_detect.py   # 模型失效检测
│   ├── backtest/
│   │   ├── __init__.py
│   │   ├── engine.py           # Walk-Forward引擎
│   │   ├── forward_bias.py     # 前视偏差检测
│   │   ├── cost_model.py       # 交易成本模型
│   │   └── metrics.py          # 绩效指标
│   ├── signals/
│   │   ├── __init__.py
│   │   ├── publisher.py
│   │   └── api.py              # FastAPI REST
│   └── pipeline/
│       ├── __init__.py
│       └── orchestrator.py     # 事件驱动主循环
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # 共享fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_event_bus.py
│   │   ├── test_bar_feature.py
│   │   ├── test_market_state.py
│   │   ├── test_setup_recog.py
│   │   ├── test_consensus.py
│   │   ├── test_rule_engine.py
│   │   ├── test_calibration.py
│   │   ├── test_fusion.py
│   │   ├── test_risk.py
│   │   └── test_backtest.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_pipeline.py
│   │   └── test_e2e.py
│   └── fixtures/
│       ├── __init__.py
│       └── sample_data.py      # 合成K线数据生成器
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 计划

### 批次 0: 项目初始化

**目标:** 创建项目骨架、依赖配置、目录结构

- [ ] **Step 1: Initialize project structure**

Create `pyproject.toml`:
```toml
[project]
name = "spas"
version = "0.1.0"
description = "Sector Probability Analysis System"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0",
    "numpy>=1.24",
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "lightgbm>=4.0",
    "scikit-learn>=1.3",
    "scipy>=1.11",
    "fastapi>=0.100",
    "uvicorn>=0.23",
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
]
```

Create `requirements.txt`:
```
pandas>=2.0
numpy>=1.24
pydantic>=2.0
pyyaml>=6.0
lightgbm>=4.0
scikit-learn>=1.3
scipy>=1.11
fastapi>=0.100
uvicorn>=0.23
pytest>=7.4
pytest-asyncio>=0.21
```

- [ ] **Step 2: Create all directories**

Run:
```bash
cd d:/stock_market
mkdir -p src/models src/event_bus src/config src/data/adapters
mkdir -p src/features src/prediction src/sentiment src/sector_linkage
mkdir -p src/risk src/backtest src/signals src/pipeline
mkdir -p config
mkdir -p tests/unit tests/integration tests/fixtures
```

- [ ] **Step 3: Create all __init__.py files**

Create empty `__init__.py` in each module directory.

- [ ] **Step 4: Create base config files**

Create `config/settings.yaml`:
```yaml
timeframes:
  daily: "1d"
  60min: "60min"
  15min: "15min"
  5min: "5min"

latency_budgets:
  5min_signal_ms: 2000
  15min_signal_ms: 5000
  60min_signal_ms: 10000

risk_constraints:
  L1_daily_stop: -0.03
  L2_weekly_stop: -0.08
  L3_monthly_stop: -0.15
  L4_max_drawdown: -0.20
  L5_single_sector_pct: 0.20
  L6_total_exposure_pct: 0.80

kelly:
  fraction: 0.25
  min_rr_ratio: 1.0

volatility_anchor:
  normal_window: 20
  current_window: 5
  decay_exponent: 0.5
  max_position_cap_at_high_vol: 0.05

market_state:
  ema_period: 20
  trend_bar_ratio_bull: 0.6
  trend_bar_ratio_bear: 0.4
  adx_period: 14
  adx_threshold: 25
  confirmation_bars: 2
  max_confidence: 0.9
  confidence_per_bar: 0.05
  initial_confidence: 0.3

setup:
  volume_shrink_ratio: 0.8
  breakout_volume_multiplier: 1.2
  breakout_body_ratio: 0.5
  quality_weights:
    pullback_similarity: 0.35
    volume_shrink: 0.30
    breakout_momentum: 0.35

calibration:
  ece_threshold: 0.01
  ece_retrain: 0.02
  ece_freeze: 0.05
  n_bins: 10
  refit_window_days: 60

backtest:
  min_samples: 1000
  min_years: 5
  walk_forward_window_months: 1
  initial_train_months: 6
  forward_bias_threshold_severe: 0.30
  forward_bias_threshold_moderate: 0.10

data_sources:
  priority: [local, tushare, akshare]
  heartbeat_interval_seconds: 30
  failure_threshold: 3
  switch_delay_ms: 500
  stale_threshold_seconds: 5
  min_daily_volume_yi: 100000000  # 1亿成交额

sentiment:
  ttl_minutes: 30
  delay_minutes: 5
  extreme_percentile: 0.95
  weights:
    official: 0.4
    media: 0.3
    research: 0.2
    social: 0.1

text_processing:
  simhash_threshold: 3
  max_age_hours: 24

sector_linkage:
  max_edges: 80
  correlation_warning: 0.80
  correlation_critical: 0.85
  correlation_emergency: 0.90
  granger_p_value: 0.05

trading_costs:
  commission_bps: 0.25  # 双向各万分之2.5
  stamp_duty_bps: 1.0   # 卖出单边千分之1
  slippage_min_bps: 0.5
  slippage_max_bps: 1.5
  impact_cost_min_bps: 1.0
  impact_cost_max_bps: 5.0
  margin_rate_annual: 0.07  # 融资年化7%

model:
  rule_confidence_threshold: 0.85
  rule_sample_threshold: 100
  max_features_per_model: 30
  transformer_layers: 2
  transformer_heads: 4
  transformer_hidden: 64
  sequence_length: 20

monitoring:
  psi_warning: 0.25
  psi_critical: 0.40
  brier_degradation_warn: 0.05
  brier_degradation_freeze: 0.10
  winrate_deviation_warn: 0.15
  winrate_deviation_freeze: 0.25
```

Create `config/sectors.yaml`:
```yaml
sectors:
  - sector_id: "801010"
    name: "农林牧渔"
    etf_code: "159825.SZ"
    index_code: "801010.SI"
    constituents:
      - code: "002714.SZ"
        name: "牧原股份"
        weight: 0.15
      - code: "300498.SZ"
        name: "温氏股份"
        weight: 0.12
    analysis_level: "basic"
    related_sectors: ["801120"]

  - sector_id: "801120"
    name: "食品饮料"
    etf_code: "515170.SH"
    index_code: "801120.SI"
    constituents:
      - code: "600519.SH"
        name: "贵州茅台"
        weight: 0.20
      - code: "000858.SZ"
        name: "五粮液"
        weight: 0.12
    analysis_level: "basic"
    related_sectors: ["801010"]
```

- [ ] **Step 5: Verify**

Run:
```bash
cd d:/stock_market && find src tests config -name "*.py" -o -name "*.yaml" | wc -l
```
Expected: all dirs and files exist

---

### 批次 1: 数据模型（对应设计文档 §5）

**目标:** 实现全部8个Pydantic v2数据模型，严格映射设计文档§5字段约束

**文件:**
- Create: `src/models/__init__.py`
- Create: `src/models/bar.py`
- Create: `src/models/feature.py`
- Create: `src/models/market_state.py`
- Create: `src/models/setup_signal.py`
- Create: `src/models/prediction.py`
- Create: `src/models/backtest.py`
- Create: `src/models/sector_config.py`
- Create: `src/models/version.py`
- Create: `tests/unit/test_models.py`

- [ ] **Step 1: 实现 BarOHLCV 和 BarAdjustment 模型**

Create `src/models/bar.py`:
```python
"""§5.1.1 K线数据模型"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class TimeFrame(str, Enum):
    M5 = "5min"
    M15 = "15min"
    M60 = "60min"
    DAY = "day"


class DataSource(str, Enum):
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    LOCAL = "local"


class BarOHLCV(BaseModel):
    """K线数据表 bar_ohlcv — §5.1.1 表1"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="K线结束时间戳")
    timeframe: TimeFrame = Field(..., description="时间框架")
    open: Decimal = Field(..., max_digits=12, decimal_places=4)
    high: Decimal = Field(..., max_digits=12, decimal_places=4)
    low: Decimal = Field(..., max_digits=12, decimal_places=4)
    close: Decimal = Field(..., max_digits=12, decimal_places=4)
    volume: int = Field(..., ge=0, description="成交量（手）")
    data_availability_time: datetime = Field(
        ..., description="数据可用时间戳 — 前视偏差防护第一道防线"
    )
    source: DataSource
    stale: bool = False
    data_version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_ohlc(self) -> "BarOHLCV":
        if self.high < max(self.open, self.close):
            raise ValueError(f"high({self.high}) must be >= max(open,close)")
        if self.low > min(self.open, self.close):
            raise ValueError(f"low({self.low}) must be <= min(open,close)")
        if self.data_availability_time < self.timestamp:
            raise ValueError(
                f"data_availability_time({self.data_availability_time}) "
                f"must be >= timestamp({self.timestamp})"
            )
        return self


class BarAdjustment(BaseModel):
    """复权因子表 bar_adjustment"""
    symbol: str = Field(..., max_length=16)
    date: datetime
    factor: Decimal = Field(..., max_digits=12, decimal_places=8)
    description: str | None = None
```

- [ ] **Step 2: 实现 FeatureVector 模型**

Create `src/models/feature.py`:
```python
"""§5.1.2 特征数据模型"""
from datetime import datetime
from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    """特征数据表 feature_vector — §5.1.2 表1"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="特征对应K线时间戳")
    timeframe: str = Field(..., max_length=8, description="时间框架(5min/15min/60min/day)")
    feature_name: str = Field(..., max_length=32, description="特征名称,如body_ratio")
    feature_value: float = Field(..., description="基于lagged价格计算的特征值")
    computation_time: datetime = Field(..., description="特征计算完成时间(审计追溯)")
    dependencies_version: str = Field(..., description="依赖数据版本摘要,如bar_v1+state_v2")
    future_function_violation: bool = Field(default=False, description="未来函数违规标记")

    class Config:
        frozen = True  # 特征向量不可变 — 保证可复现性
```

- [ ] **Step 3: 实现 MarketState 模型**

Create `src/models/market_state.py`:
```python
"""§5.1.3 市场状态模型"""
from datetime import datetime
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field


class MarketStateType(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


class RegimeType(str, Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"


class MarketState(BaseModel):
    """市场状态表 market_state — §5.1.3 表1"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="状态记录时间戳")
    timeframe: str = Field(..., max_length=8, description="时间框架")
    state: MarketStateType = Field(..., description="市场状态(bull/bear/neutral)")
    confidence: Decimal = Field(
        ..., ge=0, le=1, max_digits=4, decimal_places=3,
        description="状态置信度[0,1],随持续时间递增"
    )
    duration: int = Field(..., ge=1, description="状态持续K线数")
    regime_classification: RegimeType | None = Field(
        default=None, description="regime分类标签(trending/ranging/volatile)"
    )

    @property
    def is_trending(self) -> bool:
        return self.state in (MarketStateType.BULL, MarketStateType.BEAR)

    @property
    def is_high_confidence(self) -> bool:
        return float(self.confidence) >= 0.7
```

- [ ] **Step 4: 实现 SetupSignal 模型**

Create `src/models/setup_signal.py`:
```python
"""§5.2.1 Setup信号模型"""
from datetime import datetime
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field


class SetupType(str, Enum):
    H2 = "H2"
    L2 = "L2"
    FB = "FB"  # Failed Breakout


class SetupStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    INVALIDATED = "invalidated"


class SetupSignal(BaseModel):
    """Setup信号表 setup_signal — §5.2.1 表2"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="信号时间戳")
    setup_type: SetupType = Field(..., description="Setup类型(H2/L2/FB)")
    candidate_vs_confirmed: SetupStatus = Field(
        ..., description="候选态/确认态 — 特征工程仅用candidate态"
    )
    quality_score: Decimal = Field(
        ..., ge=0, le=1, max_digits=4, decimal_places=3,
        description="结构质量评分[0,1]"
    )
    maturity: int = Field(..., ge=0, description="成熟度(从候选态起的K线数)")
    detection_bar_index: int = Field(..., description="检测Bar序号(Walk-Forward时序对齐)")

    @property
    def is_confirmed(self) -> bool:
        return self.candidate_vs_confirmed == SetupStatus.CONFIRMED

    @property
    def is_high_quality(self) -> bool:
        return float(self.quality_score) >= 0.7
```

- [ ] **Step 5: 实现 PredictionOutput 模型**

Create `src/models/prediction.py`:
```python
"""§5.2.2 预测输出模型"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class PredictionOutput(BaseModel):
    """预测输出表 prediction_output — §5.2.2 表2"""
    symbol: str = Field(..., max_length=16, description="标的代码")
    timestamp: datetime = Field(..., description="预测时间戳")
    direction_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="上涨方向概率(Isotonic校准后)[0,1]"
    )
    target_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="目标达成概率[0,1]"
    )
    stop_prob: Decimal = Field(
        ..., ge=0, le=1, max_digits=5, decimal_places=4,
        description="止损触发概率[0,1]"
    )
    r_r_ratio: Decimal = Field(
        ..., max_digits=6, decimal_places=3,
        description="风险回报比 = target_dist/stop_dist"
    )
    expected_value: Decimal = Field(
        ..., max_digits=8, decimal_places=6,
        description="期望收益率(含交易成本的三态期望)"
    )
    setup_type: str = Field(..., max_length=8, description="触发预测的Setup类型")
    model_version: str = Field(..., max_length=32, description="产出预测的模型版本(审计)")
    raw_probability: Decimal | None = Field(
        default=None, ge=0, le=1, max_digits=5, decimal_places=4,
        description="校准前原始概率"
    )
    confidence_level: str = Field(
        default="medium", description="置信度等级(high/medium/low)"
    )
```

- [ ] **Step 6: 实现 BacktestRecord 模型**

Create `src/models/backtest.py`:
```python
"""§5.2.3 回测记录模型"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class BacktestRecord(BaseModel):
    """回测记录表 backtest_record — §5.2.3 表2"""
    version_id: str = Field(..., max_length=32, description="系统版本标识(四元组)")
    record_id: int = Field(..., description="记录序号")
    symbol: str = Field(..., max_length=16, description="标的代码")
    entry_time: datetime = Field(..., description="入场时间戳(data_availability_time已验证)")
    exit_time: datetime | None = Field(default=None, description="出场时间戳(NULL=持仓中)")
    entry_price: Decimal = Field(..., max_digits=12, decimal_places=4)
    exit_price: Decimal | None = Field(default=None, max_digits=12, decimal_places=4)
    pnl: Decimal | None = Field(default=None, max_digits=10, decimal_places=4, description="毛收益(不含成本)")
    costs: Decimal = Field(..., max_digits=10, decimal_places=4, description="总交易成本(佣金+印花税+滑点)")
    setup_type: str = Field(..., max_length=8, description="触发交易的Setup类型")
    position_size: Decimal = Field(..., max_digits=8, decimal_places=4, description="仓位比例(受凯利约束)")
    trigger_constraint: str | None = Field(default=None, max_length=16, description="触发硬约束层级(L1/L2/L3/L4)")

    @property
    def net_pnl(self) -> Decimal | None:
        if self.pnl is None:
            return None
        return self.pnl - self.costs

    @property
    def is_win(self) -> bool | None:
        if self.net_pnl is None:
            return None
        return self.net_pnl > 0
```

- [ ] **Step 7: 实现 SectorConfig 模型**

Create `src/models/sector_config.py`:
```python
"""§5.3.1 板块配置模型"""
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class ConstituentWeight(BaseModel):
    """成分股权重(含point-in-time历史权重)"""
    code: str = Field(..., max_length=16, description="成分股代码")
    name: str
    weight: Decimal = Field(..., ge=0, le=1, max_digits=6, decimal_places=4)
    effective_from: date
    effective_to: date | None = None


class SectorConfig(BaseModel):
    """板块配置表 sector_config — §5.3.1"""
    sector_id: str = Field(..., max_length=16, description="申万行业代码")
    name: str = Field(..., description="板块名称")
    etf_code: str = Field(..., max_length=16, description="代理ETF代码")
    index_code: str = Field(..., max_length=16, description="板块指数代码")
    constituents: list[ConstituentWeight] = Field(
        default_factory=list, description="成分股列表(point-in-time历史权重)"
    )
    timeframes: list[str] = Field(
        default_factory=lambda: ["5min", "15min", "60min", "day"]
    )
    analysis_level: str = Field(default="basic", description="分析深度(full/basic)")
    related_sectors: list[str] = Field(default_factory=list, description="关联板块ID列表")

    def get_constituents_at(self, target_date: date) -> list[ConstituentWeight]:
        """获取指定日期的point-in-time成分股权重 — §5.3.1幸存者偏差防护"""
        return [
            c for c in self.constituents
            if c.effective_from <= target_date
            and (c.effective_to is None or c.effective_to > target_date)
        ]
```

- [ ] **Step 8: 实现 SystemVersion 模型**

Create `src/models/version.py`:
```python
"""§5.3.2 系统版本模型"""
from datetime import datetime
from pydantic import BaseModel, Field


class SystemVersion(BaseModel):
    """系统版本表 system_version — §5.3.2"""
    version_id: str = Field(
        ..., max_length=32,
        description="系统版本标识, 如System_v3.1"
    )
    rules_version: str = Field(..., description="规则引擎版本")
    model_version: str = Field(..., description="ML模型版本(训练日期+Git Commit哈希)")
    features_version: str = Field(..., description="特征计算版本")
    data_version: str = Field(..., description="数据批次版本")
    calibration_params: dict = Field(
        default_factory=dict, description="Isotonic Regression断点与映射值"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=False)

    @property
    def full_identifier(self) -> str:
        """返回四元组完整标识 — §5.3.2"""
        return (
            f"{self.version_id}="
            f"{{rules_{self.rules_version},"
            f"model_{self.model_version},"
            f"features_{self.features_version},"
            f"data_{self.data_version}}}"
        )
```

- [ ] **Step 9: 更新 src/models/__init__.py**

```python
from src.models.bar import BarOHLCV, BarAdjustment, TimeFrame, DataSource
from src.models.feature import FeatureVector
from src.models.market_state import MarketState, MarketStateType, RegimeType
from src.models.setup_signal import SetupSignal, SetupType, SetupStatus
from src.models.prediction import PredictionOutput
from src.models.backtest import BacktestRecord
from src.models.sector_config import SectorConfig, ConstituentWeight
from src.models.version import SystemVersion
```

- [ ] **Step 10: 编写数据模型单元测试**

Create `tests/unit/test_models.py`:
```python
"""批次1: 数据模型单元测试"""
from datetime import datetime, date
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
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe=TimeFrame.M5,
            open=Decimal("3.5000"),
            high=Decimal("3.5200"),
            low=Decimal("3.4900"),
            close=Decimal("3.5100"),
            volume=1000000,
            data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
            source=DataSource.LOCAL,
        )
        assert bar.symbol == "510300.SH"
        assert bar.timeframe == TimeFrame.M5

    def test_high_must_be_gte_max_open_close(self):
        with pytest.raises(ValidationError):
            BarOHLCV(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                timeframe=TimeFrame.M5,
                open=Decimal("3.5000"),
                high=Decimal("3.4800"),  # high < open
                low=Decimal("3.4900"),
                close=Decimal("3.5100"),
                volume=1000000,
                data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                source=DataSource.LOCAL,
            )

    def test_low_must_be_lte_min_open_close(self):
        with pytest.raises(ValidationError):
            BarOHLCV(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                timeframe=TimeFrame.M5,
                open=Decimal("3.5000"),
                high=Decimal("3.5200"),
                low=Decimal("3.5100"),  # low > min(open, close)
                close=Decimal("3.4900"),
                volume=1000000,
                data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                source=DataSource.LOCAL,
            )

    def test_data_availability_time_must_be_gte_timestamp(self):
        with pytest.raises(ValidationError):
            BarOHLCV(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                timeframe=TimeFrame.M5,
                open=Decimal("3.5000"),
                high=Decimal("3.5200"),
                low=Decimal("3.4900"),
                close=Decimal("3.5100"),
                volume=1000000,
                data_availability_time=datetime(2026, 6, 24, 9, 59),  # before timestamp
                source=DataSource.LOCAL,
            )

    def test_volume_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            BarOHLCV(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                timeframe=TimeFrame.M5,
                open=Decimal("3.5000"),
                high=Decimal("3.5200"),
                low=Decimal("3.4900"),
                close=Decimal("3.5100"),
                volume=-1,  # negative volume
                data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
                source=DataSource.LOCAL,
            )

    def test_stale_default_false(self):
        bar = BarOHLCV(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe=TimeFrame.M5,
            open=Decimal("3.5000"),
            high=Decimal("3.5200"),
            low=Decimal("3.4900"),
            close=Decimal("3.5100"),
            volume=1000000,
            data_availability_time=datetime(2026, 6, 24, 10, 0, 1),
            source=DataSource.LOCAL,
        )
        assert bar.stale is False
        assert bar.data_version == 1


class TestFeatureVector:
    def test_frozen_model(self):
        fv = FeatureVector(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe="5min",
            feature_name="body_ratio",
            feature_value=0.65,
            computation_time=datetime(2026, 6, 24, 10, 0, 1),
            dependencies_version="bar_v1",
        )
        with pytest.raises(Exception):  # frozen=True prevents mutation
            fv.feature_value = 0.8

    def test_future_function_violation_default(self):
        fv = FeatureVector(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe="5min",
            feature_name="body_ratio",
            feature_value=0.65,
            computation_time=datetime(2026, 6, 24, 10, 0, 1),
            dependencies_version="bar_v1",
        )
        assert fv.future_function_violation is False


class TestMarketState:
    def test_state_transitions(self):
        ms = MarketState(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe="5min",
            state=MarketStateType.BULL,
            confidence=Decimal("0.500"),
            duration=5,
        )
        assert ms.is_trending is True
        assert ms.is_high_confidence is False

        ms_high = MarketState(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe="5min",
            state=MarketStateType.BULL,
            confidence=Decimal("0.750"),
            duration=15,
        )
        assert ms_high.is_high_confidence is True

    def test_neutral_is_not_trending(self):
        ms = MarketState(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            timeframe="5min",
            state=MarketStateType.NEUTRAL,
            confidence=Decimal("0.800"),
            duration=10,
        )
        assert ms.is_trending is False


class TestSetupSignal:
    def test_h2_candidate(self):
        s = SetupSignal(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            setup_type=SetupType.H2,
            candidate_vs_confirmed=SetupStatus.CANDIDATE,
            quality_score=Decimal("0.650"),
            maturity=0,
            detection_bar_index=100,
        )
        assert s.is_confirmed is False

    def test_h2_confirmed_high_quality(self):
        s = SetupSignal(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 5),
            setup_type=SetupType.H2,
            candidate_vs_confirmed=SetupStatus.CONFIRMED,
            quality_score=Decimal("0.850"),
            maturity=3,
            detection_bar_index=103,
        )
        assert s.is_confirmed is True
        assert s.is_high_quality is True

    def test_l2_and_fb_types(self):
        for st in [SetupType.L2, SetupType.FB]:
            s = SetupSignal(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                setup_type=st,
                candidate_vs_confirmed=SetupStatus.CANDIDATE,
                quality_score=Decimal("0.500"),
                maturity=0,
                detection_bar_index=1,
            )
            assert s.setup_type == st


class TestPredictionOutput:
    def test_full_prediction(self):
        p = PredictionOutput(
            symbol="510300.SH",
            timestamp=datetime(2026, 6, 24, 10, 0),
            direction_prob=Decimal("0.6500"),
            target_prob=Decimal("0.5500"),
            stop_prob=Decimal("0.1500"),
            r_r_ratio=Decimal("2.500"),
            expected_value=Decimal("0.008500"),
            setup_type="H2",
            model_version="model_20260615_a1b2c3",
            raw_probability=Decimal("0.6200"),
            confidence_level="high",
        )
        assert float(p.direction_prob) == pytest.approx(0.65)
        assert float(p.r_r_ratio) == pytest.approx(2.5)

    def test_direction_prob_bounds(self):
        with pytest.raises(ValidationError):
            PredictionOutput(
                symbol="510300.SH",
                timestamp=datetime(2026, 6, 24, 10, 0),
                direction_prob=Decimal("1.5000"),  # > 1
                target_prob=Decimal("0.5000"),
                stop_prob=Decimal("0.1000"),
                r_r_ratio=Decimal("2.000"),
                expected_value=Decimal("0.010000"),
                setup_type="H2",
                model_version="v1",
            )


class TestBacktestRecord:
    def test_win_record(self):
        rec = BacktestRecord(
            version_id="System_v3.1",
            record_id=1,
            symbol="510300.SH",
            entry_time=datetime(2026, 6, 24, 10, 0),
            exit_time=datetime(2026, 6, 24, 11, 0),
            entry_price=Decimal("3.5000"),
            exit_price=Decimal("3.5500"),
            pnl=Decimal("0.0500"),
            costs=Decimal("0.0025"),
            setup_type="H2",
            position_size=Decimal("0.0800"),
        )
        assert rec.is_win is True
        assert float(rec.net_pnl) == pytest.approx(0.0475)

    def test_loss_record(self):
        rec = BacktestRecord(
            version_id="System_v3.1",
            record_id=2,
            symbol="510300.SH",
            entry_time=datetime(2026, 6, 24, 10, 0),
            exit_time=datetime(2026, 6, 24, 10, 30),
            entry_price=Decimal("3.5000"),
            exit_price=Decimal("3.4500"),
            pnl=Decimal("-0.0500"),
            costs=Decimal("0.0025"),
            setup_type="L2",
            position_size=Decimal("0.0500"),
            trigger_constraint="L1",
        )
        assert rec.is_win is False
        assert float(rec.net_pnl) == pytest.approx(-0.0525)


class TestSectorConfig:
    def test_point_in_time_constituents(self):
        c1 = ConstituentWeight(
            code="002714.SZ", name="牧原股份",
            weight=Decimal("0.15"),
            effective_from=date(2020, 1, 1),
            effective_to=date(2024, 12, 31),
        )
        c2 = ConstituentWeight(
            code="002714.SZ", name="牧原股份",
            weight=Decimal("0.18"),
            effective_from=date(2025, 1, 1),
            effective_to=None,
        )
        sector = SectorConfig(
            sector_id="801010",
            name="农林牧渔",
            etf_code="159825.SZ",
            index_code="801010.SI",
            constituents=[c1, c2],
        )
        # 2024年中应该使用c1
        mid_2024 = date(2024, 6, 15)
        constituents = sector.get_constituents_at(mid_2024)
        assert len(constituents) == 1
        assert constituents[0].weight == Decimal("0.15")

        # 2025年中应该使用c2
        mid_2025 = date(2025, 6, 15)
        constituents = sector.get_constituents_at(mid_2025)
        assert len(constituents) == 1
        assert constituents[0].weight == Decimal("0.18")


class TestSystemVersion:
    def test_full_identifier(self):
        sv = SystemVersion(
            version_id="System_v3.1",
            rules_version="v2.3",
            model_version="20240115_a1b2c3",
            features_version="v1.5",
            data_version="2024q1",
        )
        ident = sv.full_identifier
        assert "System_v3.1" in ident
        assert "rules_v2.3" in ident
        assert "model_20240115_a1b2c3" in ident
        assert "features_v1.5" in ident
        assert "data_2024q1" in ident
```

- [ ] **Step 11: Run tests**

```bash
cd d:/stock_market && python -m pytest tests/unit/test_models.py -v
```
Expected: All tests PASS

- [ ] **Step 12: Verify data model compliance with design doc §5**

Check each model against:
- §5.1.1 Table 1: bar_ohlcv fields, constraints ✅
- §5.1.2 Table 1: feature_vector fields, frozen ✅
- §5.1.3 Table 1: market_state fields, confidence range ✅
- §5.2.1 Table 2: setup_signal fields, candidate/confirmed ✅
- §5.2.2 Table 2: prediction_output fields, expected_value formula ✅
- §5.2.3 Table 2: backtest_record fields, version_id ✅
- §5.3.1: sector_config point-in-time weights ✅
- §5.3.2: system_version 四子版本 ✅

---

### 批次 2: 事件总线 + 配置加载

**目标:** 实现Redis Streams语义的内部事件总线 + YAML配置加载

**文件:**
- Create: `src/event_bus/__init__.py`
- Create: `src/event_bus/events.py`
- Create: `src/event_bus/stream.py`
- Create: `src/config/__init__.py`
- Create: `src/config/loader.py`
- Create: `tests/unit/test_event_bus.py`

- [ ] **Step 1: 定义事件类型**

Create `src/event_bus/events.py`:
```python
"""§7.1.1 事件类型定义 — 严格对应设计文档四类核心事件"""
from datetime import datetime
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class EventType(str, Enum):
    BAR_CLOSE = "bar_close"
    FEATURE_COMPUTE = "feature_compute"
    STATE_TRANSITION = "state_transition"
    SETUP_DETECTED = "setup_detected"
    CONSENSUS_UPDATE = "consensus_update"
    PREDICTION_TRIGGER = "prediction_trigger"
    PREDICTION = "prediction"
    SENTIMENT_CACHED = "sentiment_cached"
    SIGNAL = "signal"


class EventHeader(BaseModel):
    """统一事件消息头 — §7.1.1"""
    trace_id: str = Field(default_factory=lambda: uuid4().hex[:16])
    event_id: str = Field(default_factory=lambda: uuid4().hex)
    parent_event_id: str | None = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    version: str = "v1.0"
    source_service: str
    data_version: str = "v1"


class BarCloseEvent(BaseModel):
    """K线闭合事件 — 事件流根节点 §7.1.1"""
    header: EventHeader
    symbol: str
    timeframe: str
    bar_timestamp: datetime
    data_availability_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class FeatureComputeEvent(BaseModel):
    """特征计算事件 — BarFeatureSvc输出 §7.1.1"""
    header: EventHeader
    symbol: str
    timeframe: str
    feature_name: str
    feature_value: float
    is_stale: bool = False
    decay_weight: float = 1.0


class StateTransitionEvent(BaseModel):
    """状态转移事件 — MarketStateSvc输出 §7.1.1"""
    header: EventHeader
    symbol: str
    timeframe: str
    previous_state: str | None
    new_state: str
    confidence: float
    duration: int


class SetupDetectedEvent(BaseModel):
    """Setup检测事件 — SetupRecogSvc输出 §7.1.1"""
    header: EventHeader
    symbol: str
    timeframe: str
    setup_type: str
    status: str  # candidate/confirmed/invalidated
    quality_score: float
    maturity: int


class ConsensusUpdateEvent(BaseModel):
    """板块一致性事件 — ConsensusSvc输出 §7.1.1"""
    header: EventHeader
    sector_id: str
    up_ratio: float
    momentum_median: float
    leader_corr: float | None
    is_stale: bool = False


class PredictionEvent(BaseModel):
    """预测事件 — 模型服务输出 §7.1.1"""
    header: EventHeader
    symbol: str
    direction_prob: float
    calibrated_prob: float
    raw_prob: float | None
    confidence_level: str
    setup_type: str
    expected_value: float
    r_r_ratio: float


class SignalEvent(BaseModel):
    """最终交易信号事件 — §7.3.1"""
    header: EventHeader
    symbol: str
    setup_type: str
    direction: str
    raw_probability: float
    adjusted_probability: float
    risk_reward_ratio: float
    expected_return: float
    confidence_level: str
    deviation_analysis: str | None = None
```

- [ ] **Step 2: 实现事件总线**

Create `src/event_bus/stream.py`:
```python
"""§7.1.1 Redis Streams语义的内部事件总线实现"""
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, AsyncIterator


class EventStream:
    """内部事件总线 — 与Redis Streams API兼容:

    - publish(stream, event)  ≈ Redis XADD
    - subscribe(stream, group, consumer) ≈ Redis XREADGROUP
    """

    def __init__(self):
        self._streams: dict[str, list[tuple[str, Any]]] = defaultdict(list)
        self._consumer_groups: dict[str, dict[str, int]] = defaultdict(dict)
        self._pending: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
        self._cond = asyncio.Condition()

    async def publish(self, stream: str, event: Any, event_id: str | None = None) -> str:
        """发布事件到指定流 — XADD语义"""
        async with self._cond:
            eid = event_id or f"{int(datetime.now().timestamp() * 1000)}-0"
            self._streams[stream].append((eid, event))
            self._cond.notify_all()
            return eid

    async def subscribe(
        self,
        stream: str,
        group: str = "default",
        consumer: str = "default",
        block_ms: int = 5000,
    ) -> AsyncIterator[tuple[str, Any]]:
        """订阅流事件 — XREADGROUP语义: 消费者组, 未ack消息重投递"""
        # 初始化消费者组
        if group not in self._consumer_groups[stream]:
            self._consumer_groups[stream][group] = 0

        last_idx = self._consumer_groups[stream][group]

        while True:
            async with self._cond:
                # 先检查是否有pending消息
                pending = self._pending[stream].get(f"{group}:{consumer}", [])
                if pending:
                    idx = pending.pop(0)
                    if idx < len(self._streams[stream]):
                        eid, event = self._streams[stream][idx]
                        yield (eid, event)
                        continue

                # 等待新消息
                current_len = len(self._streams[stream])
                if current_len <= last_idx:
                    try:
                        await asyncio.wait_for(
                            self._cond.wait(),
                            timeout=block_ms / 1000,
                        )
                    except asyncio.TimeoutError:
                        continue
                    current_len = len(self._streams[stream])

                # 消费新消息
                while last_idx < current_len:
                    eid, event = self._streams[stream][last_idx]
                    last_idx += 1
                    yield (eid, event)

                self._consumer_groups[stream][group] = last_idx

    async def ack(self, stream: str, group: str, consumer: str, event_id: str):
        """确认消息处理完成 — XACK语义"""
        pass  # 简化实现: 消费即确认

    async def stream_length(self, stream: str) -> int:
        """获取流长度 — XLEN语义"""
        async with self._cond:
            return len(self._streams[stream])

    async def reset(self):
        """清空所有流(用于测试)"""
        async with self._cond:
            self._streams.clear()
            self._consumer_groups.clear()
            self._pending.clear()
```

- [ ] **Step 3: 实现配置加载器**

Create `src/config/loader.py`:
```python
"""配置管理 — 集中式YAML配置加载 + Pydantic校验"""
from pathlib import Path
from pydantic import BaseModel, Field


class RiskConstraintsConfig(BaseModel):
    L1_daily_stop: float = -0.03
    L2_weekly_stop: float = -0.08
    L3_monthly_stop: float = -0.15
    L4_max_drawdown: float = -0.20
    L5_single_sector_pct: float = 0.20
    L6_total_exposure_pct: float = 0.80


class KellyConfig(BaseModel):
    fraction: float = 0.25
    min_rr_ratio: float = 1.0


class VolatilityAnchorConfig(BaseModel):
    normal_window: int = 20
    current_window: int = 5
    decay_exponent: float = 0.5
    max_position_cap_at_high_vol: float = 0.05


class MarketStateConfig(BaseModel):
    ema_period: int = 20
    trend_bar_ratio_bull: float = 0.6
    trend_bar_ratio_bear: float = 0.4
    adx_period: int = 14
    adx_threshold: int = 25
    confirmation_bars: int = 2
    max_confidence: float = 0.9
    confidence_per_bar: float = 0.05
    initial_confidence: float = 0.3


class SetupConfig(BaseModel):
    volume_shrink_ratio: float = 0.8
    breakout_volume_multiplier: float = 1.2
    breakout_body_ratio: float = 0.5
    quality_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "pullback_similarity": 0.35,
            "volume_shrink": 0.30,
            "breakout_momentum": 0.35,
        }
    )


class CalibrationConfig(BaseModel):
    ece_threshold: float = 0.01
    ece_retrain: float = 0.02
    ece_freeze: float = 0.05
    n_bins: int = 10
    refit_window_days: int = 60


class BacktestConfig(BaseModel):
    min_samples: int = 1000
    min_years: int = 5
    walk_forward_window_months: int = 1
    initial_train_months: int = 6
    forward_bias_threshold_severe: float = 0.30
    forward_bias_threshold_moderate: float = 0.10


class TradingCostsConfig(BaseModel):
    commission_bps: float = 0.25
    stamp_duty_bps: float = 1.0
    slippage_min_bps: float = 0.5
    slippage_max_bps: float = 1.5
    impact_cost_min_bps: float = 1.0
    impact_cost_max_bps: float = 5.0
    margin_rate_annual: float = 0.07


class AppConfig(BaseModel):
    """全局应用配置"""
    risk_constraints: RiskConstraintsConfig = Field(default_factory=RiskConstraintsConfig)
    kelly: KellyConfig = Field(default_factory=KellyConfig)
    volatility_anchor: VolatilityAnchorConfig = Field(default_factory=VolatilityAnchorConfig)
    market_state: MarketStateConfig = Field(default_factory=MarketStateConfig)
    setup: SetupConfig = Field(default_factory=SetupConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    trading_costs: TradingCostsConfig = Field(default_factory=TradingCostsConfig)


def load_config(config_dir: str | Path = "config") -> AppConfig:
    """从YAML文件加载配置 — 支持环境覆盖"""
    import yaml
    config_path = Path(config_dir) / "settings.yaml"
    if not config_path.exists():
        return AppConfig()

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    sections = {}
    section_map = {
        "risk_constraints": RiskConstraintsConfig,
        "kelly": KellyConfig,
        "volatility_anchor": VolatilityAnchorConfig,
        "market_state": MarketStateConfig,
        "setup": SetupConfig,
        "calibration": CalibrationConfig,
        "backtest": BacktestConfig,
        "trading_costs": TradingCostsConfig,
    }

    for key, cls in section_map.items():
        if key in raw:
            sections[key] = cls(**raw[key])

    return AppConfig(**sections)
```

- [ ] **Step 4: 编写事件总线 + 配置测试**

Create `tests/unit/test_event_bus.py`:
```python
"""批次2: 事件总线 + 配置加载单元测试"""
import asyncio
import pytest
from src.event_bus.stream import EventStream
from src.event_bus.events import (
    EventHeader, BarCloseEvent, FeatureComputeEvent,
    StateTransitionEvent, SetupDetectedEvent, PredictionEvent,
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
            results["a"] = event
            break
        async for eid, event in bus.subscribe("stream_b", block_ms=100):
            results["b"] = event
            break

        assert results["a"] == {"data": "a"}
        assert results["b"] == {"data": "b"}

    @pytest.mark.asyncio
    async def test_bar_close_event_flow(self):
        """模拟完整的BarCloseEvent → 事件链路 §7.1.1"""
        bus = EventStream()
        header = EventHeader(source_service="data_fetcher")
        bar_event = BarCloseEvent(
            header=header,
            symbol="510300.SH",
            timeframe="5min",
            bar_timestamp="2026-06-24T10:00:00",
            data_availability_time="2026-06-24T10:00:01",
            open=3.5, high=3.52, low=3.49, close=3.51, volume=1000000,
        )

        await bus.publish("stream:bar_close", bar_event)

        async for eid, event in bus.subscribe("stream:bar_close", block_ms=100):
            assert isinstance(event, BarCloseEvent)
            assert event.symbol == "510300.SH"
            assert event.timeframe == "5min"
            assert event.close == 3.51
            break

    @pytest.mark.asyncio
    async def test_consumer_group_isolation(self):
        """测试消费者组隔离 — 每个组独立消费"""
        bus = EventStream()
        await bus.publish("multi", {"msg": 1})
        await bus.publish("multi", {"msg": 2})

        # 两个独立的消费者组各自消费全部消息
        group_a_msgs = []
        group_b_msgs = []

        async for eid, event in bus.subscribe("multi", group="group_a", block_ms=100):
            group_a_msgs.append(event)
            if len(group_a_msgs) >= 2:
                break

        async for eid, event in bus.subscribe("multi", group="group_b", consumer="c2", block_ms=100):
            group_b_msgs.append(event)
            if len(group_b_msgs) >= 2:
                break

        assert len(group_a_msgs) == 2
        assert len(group_b_msgs) == 2


class TestConfigLoader:
    def test_default_config(self):
        config = AppConfig()
        assert config.risk_constraints.L1_daily_stop == -0.03
        assert config.kelly.fraction == 0.25
        assert config.market_state.adx_threshold == 25
        assert config.calibration.ece_threshold == 0.01

    def test_load_from_yaml(self):
        config = load_config("config")
        assert isinstance(config, AppConfig)
        # 验证从YAML加载的覆盖值
        assert config.market_state.confirmation_bars == 2

    def test_trading_costs_config(self):
        config = AppConfig()
        assert config.trading_costs.commission_bps == 0.25
        assert config.trading_costs.stamp_duty_bps == 1.0
```

- [ ] **Step 5: Run tests**

```bash
cd d:/stock_market && python -m pytest tests/unit/test_event_bus.py -v
```
Expected: All tests PASS

- [ ] **Step 6: Run all existing tests (regression)**

```bash
cd d:/stock_market && python -m pytest tests/ -v
```
Expected: All tests (models + event_bus) PASS

---

### 批次 3: 数据采集层（对应设计文档 §4.1）

**目标:** 实现UDAI统一接口 + 3个数据源适配器 + 多源协调器 + 复权处理 + 质量监控

**文件:**
- Create: `src/data/__init__.py`
- Create: `src/data/adapters/__init__.py`
- Create: `src/data/adapters/base.py`
- Create: `src/data/adapters/tushare.py`
- Create: `src/data/adapters/akshare.py`
- Create: `src/data/adapters/local.py`
- Create: `src/data/fetcher.py`
- Create: `src/data/adjustment.py`
- Create: `src/data/quality.py`
- Create: `tests/fixtures/sample_data.py`
- Create: `tests/unit/test_data_adapters.py`

- [ ] **Step 1: 创建测试数据生成器**

Create `tests/fixtures/sample_data.py`:
```python
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
) -> list[BarOHLCV]:
    """生成合成K线数据

    Args:
        symbol: 标的代码
        timeframe: 时间框架
        n_bars: K线数量
        start_price: 起始价格
        volatility: 波动率(单Bar标准差)
        trend: 趋势漂移(每Bar)
        seed: 随机种子(可复现)
    """
    rng = np.random.default_rng(seed)
    returns = rng.normal(trend, volatility, n_bars)
    prices = start_price * np.exp(np.cumsum(returns))

    base_time = datetime(2026, 6, 24, 9, 30)
    bars = []
    for i in range(n_bars):
        p_open = prices[i]
        p_close = prices[i] * (1 + rng.normal(0, volatility * 0.5))
        p_high = max(p_open, p_close) * (1 + abs(rng.normal(0, volatility * 0.3)))
        p_low = min(p_open, p_close) * (1 - abs(rng.normal(0, volatility * 0.3)))
        volume = int(abs(rng.normal(1_000_000, 300_000)))

        bar = BarOHLCV(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=5 * i),
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


def generate_trend_bars(
    symbol: str = "510300.SH",
    n_bars: int = 50,
    direction: str = "up",
    seed: int = 42,
) -> list[BarOHLCV]:
    """生成趋势K线序列(用于MarketStateSvc测试)"""
    trend_val = 0.002 if direction == "up" else -0.002
    return generate_bars(
        symbol=symbol,
        n_bars=n_bars,
        start_price=3.5,
        volatility=0.005,
        trend=trend_val,
        seed=seed,
    )


def generate_swing_bars(
    symbol: str = "510300.SH",
    n_bars: int = 100,
    seed: int = 42,
) -> list[BarOHLCV]:
    """生成震荡K线序列(包含两腿回撤结构,用于SetupRecogSvc测试)"""
    rng = np.random.default_rng(seed)
    prices = [3.5]
    # 先上涨
    for i in range(20):
        prices.append(prices[-1] * (1 + abs(rng.normal(0.003, 0.001))))
    # 第一腿回撤
    for i in range(10):
        prices.append(prices[-1] * (1 - abs(rng.normal(0.002, 0.001))))
    # 小幅反弹
    for i in range(5):
        prices.append(prices[-1] * (1 + abs(rng.normal(0.001, 0.0005))))
    # 第二腿回撤
    for i in range(8):
        prices.append(prices[-1] * (1 - abs(rng.normal(0.0015, 0.0008))))
    # 突破
    for i in range(10):
        prices.append(prices[-1] * (1 + abs(rng.normal(0.004, 0.002))))

    base_time = datetime(2026, 6, 24, 9, 30)
    bars = []
    for i, price in enumerate(prices):
        bar = BarOHLCV(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=5 * i),
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
```

- [ ] **Step 2: 实现UDAI统一接口**

Create `src/data/adapters/base.py`:
```python
"""§4.1.1 UDAI统一数据抽象接口"""
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd


class DataAdapter(ABC):
    """统一数据抽象接口 — 屏蔽Tushare/AKShare/本地三源差异

    所有适配器实现此接口，确保主备切换对上层透明。
    返回标准化DataFrame: open/high/low/close/volume/factor 六字段
    """

    source_name: str = "base"

    @abstractmethod
    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """获取K线数据 — 标准化接口 §4.1.1

        Returns:
            DataFrame with columns: open, high, low, close, volume, factor
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查 — 心跳检测(30秒间隔) §4.1.1"""
        ...

    async def get_data_availability_time(self, symbol: str, freq: str) -> datetime | None:
        """获取最新数据可用时间 — 前视偏差防护"""
        return datetime.now()
```

- [ ] **Step 3: 实现本地Parquet适配器**

Create `src/data/adapters/local.py`:
```python
"""本地Parquet缓存适配器 — 第一优先级(零延迟) §4.1.1 表1"""
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.data.adapters.base import DataAdapter


class LocalAdapter(DataAdapter):
    source_name = "local"

    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        file_path = self.data_dir / f"{symbol}_{freq}.parquet"
        if not file_path.exists():
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

        df = pd.read_parquet(file_path)
        if df.empty:
            return df

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            if start:
                df = df[df["timestamp"] >= start]
            if end:
                df = df[df["timestamp"] <= end]

        return df

    async def save_bars(self, symbol: str, freq: str, df: pd.DataFrame):
        """保存K线数据到本地Parquet"""
        file_path = self.data_dir / f"{symbol}_{freq}.parquet"
        df.to_parquet(file_path, index=False)

    async def health_check(self) -> bool:
        return self.data_dir.exists()
```

- [ ] **Step 4: 实现Tushare Pro适配器（框架）**

Create `src/data/adapters/tushare.py`:
```python
"""Tushare Pro适配器 — 主力数据源(第二优先级) §4.1.1 表1"""
from datetime import datetime
import pandas as pd
from src.data.adapters.base import DataAdapter


class TushareAdapter(DataAdapter):
    source_name = "tushare"

    def __init__(self, token: str | None = None):
        self.token = token
        self._healthy = True

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """获取K线数据 — §7.2.1

        分钟级数据需本地复权补偿(见adjustment模块)
        """
        # 生产环境: 调用 tushare.pro_bar()
        # 开发/测试环境: 返回空DataFrame(由local adapter提供数据)
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_check(self) -> bool:
        """心跳检测(30秒间隔) — §4.1.1"""
        try:
            # 生产环境: 调用 tushare 心跳API
            return self._healthy
        except Exception:
            self._healthy = False
            return False
```

- [ ] **Step 5: 实现AKShare适配器（框架）**

Create `src/data/adapters/akshare.py`:
```python
"""AKShare适配器 — 备用数据源(第三优先级) §4.1.1 表1, §7.2.2"""
from datetime import datetime
import pandas as pd
from src.data.adapters.base import DataAdapter


class AKShareAdapter(DataAdapter):
    source_name = "akshare"

    def __init__(self):
        self._healthy = True
        self._latency_seconds = 3  # AKShare数据延迟3-5秒 §7.2.2

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        # 生产环境: 调用 akshare API
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_check(self) -> bool:
        return self._healthy

    @property
    def data_delay_seconds(self) -> int:
        return self._latency_seconds
```

- [ ] **Step 6: 实现多源协调器**

Create `src/data/fetcher.py`:
```python
"""§4.1.1 多源数据协调器 — 健康状态机 + 主备自动切换"""
from datetime import datetime
import asyncio
import logging
import pandas as pd
from src.data.adapters.base import DataAdapter
from src.data.adapters.local import LocalAdapter
from src.data.adapters.tushare import TushareAdapter
from src.data.adapters.akshare import AKShareAdapter

logger = logging.getLogger(__name__)


class DataFetcher:
    """多数据源协调器 — §4.1.1

    特性:
    - 优先级顺序: 本地缓存 > Tushare Pro > AKShare
    - 心跳检测(30秒间隔)，连续3次失败标记不可用
    - 主备自动切换，切换延迟<500ms
    """

    def __init__(self):
        self.adapters: list[DataAdapter] = []
        self._health_status: dict[str, int] = {}  # 连续失败计数
        self._failure_threshold = 3

    def register(self, adapter: DataAdapter, priority: int):
        """注册数据源适配器 — priority越小优先级越高"""
        self.adapters.append(adapter)
        self.adapters.sort(key=lambda a: priority)
        self._health_status[adapter.source_name] = 0

    @classmethod
    def with_defaults(cls, data_dir: str = "data") -> "DataFetcher":
        """创建默认三源配置 — 本地>Tushare>AKShare"""
        fetcher = cls()
        fetcher.register(LocalAdapter(data_dir), priority=0)
        fetcher.register(TushareAdapter(), priority=1)
        fetcher.register(AKShareAdapter(), priority=2)
        return fetcher

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """获取K线数据 — 自动主备切换 §4.1.1"""
        for adapter in self.adapters:
            if self._health_status.get(adapter.source_name, 0) >= self._failure_threshold:
                continue

            try:
                start_time = datetime.now()
                df = await adapter.get_bars(symbol, freq, start, end)
                elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

                if elapsed_ms > 5000:
                    logger.warning(
                        f"Adapter {adapter.source_name} slow: {elapsed_ms:.0f}ms"
                    )

                if df.empty and adapter.source_name != "local":
                    continue  # API源返回空，继续尝试下一个

                self._health_status[adapter.source_name] = 0
                return df

            except Exception as e:
                self._health_status[adapter.source_name] = (
                    self._health_status.get(adapter.source_name, 0) + 1
                )
                logger.error(f"Adapter {adapter.source_name} failed: {e}")
                continue

        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    async def health_monitor(self):
        """后台健康监控 — 心跳检测(30秒间隔) §4.1.1"""
        while True:
            for adapter in self.adapters:
                try:
                    healthy = await adapter.health_check()
                    if not healthy:
                        self._health_status[adapter.source_name] += 1
                    else:
                        self._health_status[adapter.source_name] = 0
                except Exception:
                    self._health_status[adapter.source_name] += 1
            await asyncio.sleep(30)
```

- [ ] **Step 7: 实现复权处理**

Create `src/data/adjustment.py`:
```python
"""§4.1.3 分钟级复权处理"""
from datetime import datetime, date
from decimal import Decimal
import pandas as pd


class PriceAdjuster:
    """分钟级前复权价格计算器 — §4.1.3

    Tushare Pro分钟数据不提供复权价格，需基于日线复权因子自计算。

    公式: P_adj_min = P_raw_min × factor_t / factor_base
    """

    def __init__(self):
        self._daily_factors: dict[str, dict[date, Decimal]] = {}

    def set_daily_factors(self, symbol: str, factors: dict[date, Decimal], base_date: date):
        """设置日线复权因子 — 每日开盘前获取"""
        self._daily_factors[symbol] = factors
        self._base_date = base_date

    def adjust_price(
        self,
        symbol: str,
        raw_price: Decimal,
        trade_date: date,
        base_factor: Decimal | None = None,
    ) -> Decimal:
        """计算分钟级前复权价格

        Args:
            symbol: 标的代码
            raw_price: 原始分钟价格
            trade_date: 交易日
            base_factor: 基准日复权因子(默认使用第一个有效因子)

        Returns:
            前复权价格。若除权日因子缺失，返回NaN标记
        """
        factors = self._daily_factors.get(symbol, {})
        factor_t = factors.get(trade_date)

        if factor_t is None:
            return Decimal("NaN")  # §4.1.3: 除权日标记NaN

        if base_factor is None:
            base_factor = list(factors.values())[0] if factors else Decimal("1")

        if base_factor == 0:
            return Decimal("NaN")

        return raw_price * factor_t / base_factor

    def adjust_dataframe(
        self,
        symbol: str,
        df: pd.DataFrame,
        price_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """对DataFrame中的价格列执行复权"""
        if price_columns is None:
            price_columns = ["open", "high", "low", "close"]

        df = df.copy()
        for col in price_columns:
            if col in df.columns:
                if "trade_date" in df.columns:
                    df[col] = df.apply(
                        lambda row: self.adjust_price(
                            symbol, Decimal(str(row[col])), row["trade_date"].date()
                        ),
                        axis=1,
                    )
        return df
```

- [ ] **Step 8: 实现数据质量监控**

Create `src/data/quality.py`:
```python
"""§4.1.4 数据质量监控 — 完整性/时效性/异常值"""
from datetime import datetime, timedelta
import pandas as pd


class DataQualityMonitor:
    """数据质量监控器 — §4.1.4

    监控维度:
    - 完整性: 每批次数据缺失率
    - 时效性: 数据获取延迟P50/P99/P99.9
    - 异常值: 单Bar涨跌幅超限/成交量超限
    """

    def __init__(
        self,
        max_missing_rate: float = 0.05,
        max_delay_p99_ms: float = 30000,
        max_bar_change_pct: float = 10.0,
        max_volume_multiplier: float = 5.0,
    ):
        self.max_missing_rate = max_missing_rate
        self.max_delay_p99_ms = max_delay_p99_ms
        self.max_bar_change_pct = max_bar_change_pct
        self.max_volume_multiplier = max_volume_multiplier

    def check_completeness(self, df: pd.DataFrame, expected_count: int) -> tuple[bool, float]:
        """完整性检查 — §4.1.4: 缺失率>5%丢弃批次"""
        actual_count = len(df)
        missing_rate = 1.0 - (actual_count / expected_count) if expected_count > 0 else 1.0
        return missing_rate <= self.max_missing_rate, missing_rate

    def check_timeliness(self, latencies_ms: list[float]) -> dict:
        """时效性检查 — §4.1.4: P99>30秒降级备用源"""
        if not latencies_ms:
            return {"p50": 0, "p99": 0, "p999": 0, "pass": True}

        sorted_lat = sorted(latencies_ms)
        p50 = sorted_lat[len(sorted_lat) // 2]
        p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
        p999 = sorted_lat[int(len(sorted_lat) * 0.999)]

        return {
            "p50": p50,
            "p99": p99,
            "p999": p999,
            "pass": p99 <= self.max_delay_p99_ms,
        }

    def detect_anomalies(self, df: pd.DataFrame, avg_volume_20d: float) -> pd.Series:
        """异常值检测 — §4.1.4

        Returns:
            boolean Series, True=异常Bar(不参与特征计算)
        """
        anomalies = pd.Series(False, index=df.index)

        if "close" in df.columns and "open" in df.columns:
            change_pct = abs((df["close"] - df["open"]) / df["open"] * 100)
            anomalies |= change_pct > self.max_bar_change_pct

        if "volume" in df.columns and avg_volume_20d > 0:
            anomalies |= df["volume"] > avg_volume_20d * self.max_volume_multiplier

        return anomalies
```

- [ ] **Step 9: 编写数据采集测试**

Create `tests/unit/test_data_adapters.py`:
```python
"""批次3: 数据采集层单元测试"""
import asyncio
import pytest
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
        import pandas as pd
        df = pd.DataFrame([{
            "timestamp": b.timestamp,
            "open": float(b.open),
            "high": float(b.high),
            "low": float(b.low),
            "close": float(b.close),
            "volume": b.volume,
            "factor": 1.0,
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
        # 保存一些数据到本地
        adapter = LocalAdapter(data_dir=str(tmp_path))
        bars = generate_bars(n_bars=5)
        import pandas as pd
        df = pd.DataFrame([{
            "timestamp": b.timestamp,
            "open": float(b.open),
            "high": float(b.high),
            "low": float(b.low),
            "close": float(b.close),
            "volume": b.volume,
            "factor": 1.0,
        } for b in bars])
        await adapter.save_bars("510300.SH", "5min", df)

        df = await fetcher.get_bars("510300.SH", "5min")
        assert len(df) == 5


class TestPriceAdjuster:
    def test_basic_adjustment(self):
        from decimal import Decimal
        from datetime import date

        adjuster = PriceAdjuster()
        adjuster.set_daily_factors(
            "510300.SH",
            {
                date(2026, 6, 24): Decimal("1.5"),
                date(2026, 6, 25): Decimal("1.0"),
            },
            base_date=date(2026, 6, 24),
        )

        # 基准日: factor_t=1.5, base_factor=1.5, price不变
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 24))
        assert float(adj) == pytest.approx(100.0)

        # 除权后: factor_t=1.0, base_factor=1.5
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 25))
        assert float(adj) == pytest.approx(100.0 * 1.0 / 1.5)

    def test_missing_factor_returns_nan(self):
        from decimal import Decimal
        from datetime import date

        adjuster = PriceAdjuster()
        adjuster.set_daily_factors("510300.SH", {}, base_date=date(2026, 6, 24))
        adj = adjuster.adjust_price("510300.SH", Decimal("100"), date(2026, 6, 25))
        assert adj.is_nan()  # §4.1.3: 除权日标记NaN


class TestDataQualityMonitor:
    def test_completeness_pass(self):
        monitor = DataQualityMonitor()
        import pandas as pd
        df = pd.DataFrame({"a": range(95)})
        ok, rate = monitor.check_completeness(df, expected_count=100)
        assert ok  # 5% missing is OK
        assert rate == pytest.approx(0.05)

    def test_completeness_fail(self):
        monitor = DataQualityMonitor()
        import pandas as pd
        df = pd.DataFrame({"a": range(90)})
        ok, rate = monitor.check_completeness(df, expected_count=100)
        assert not ok  # 10% > 5% threshold

    def test_anomaly_detection(self):
        monitor = DataQualityMonitor(max_bar_change_pct=10.0)
        import pandas as pd
        df = pd.DataFrame({
            "open": [100, 100, 100],
            "close": [102, 115, 98],  # 第2行: 15%涨幅异常
            "volume": [1000000, 1000000, 1000000],
        })
        anomalies = monitor.detect_anomalies(df, avg_volume_20d=1000000)
        assert anomalies.iloc[1]  # 15% > 10%, 应标记异常
        assert not anomalies.iloc[0]
```

- [ ] **Step 10: Run tests**

```bash
cd d:/stock_market && python -m pytest tests/unit/test_data_adapters.py -v
```
Expected: All tests PASS

- [ ] **Step 11: Run all regression tests**

```bash
cd d:/stock_market && python -m pytest tests/ -v
```
Expected: All existing tests still PASS

---

... (plan continues with Batches 4-13)

由于此实施计划篇幅极长（13批次、50+任务步骤），我将在执行过程中逐步展开后续批次。以下是后续批次的摘要：

| 批次 | 核心文件数 | 关键交付 |
|------|----------|---------|
| 4 | 3 | BarFeatureSvc — K线微观结构6维特征（§4.2.1） |
| 5 | 3 | MarketStateSvc — EMA20+ADX>25状态机（§4.2.2） |
| 6 | 3 | SetupRecogSvc — H2/L2/FB候选→确认状态机（§4.2.3） |
| 7 | 3 | ConsensusSvc — 板块一致性+stale降级（§4.2.4） |
| 8 | 3 | RuleEngine — 多维规则特征输出（§4.3.1） |
| 9 | 4 | MLModel + Calibration — LightGBM + Isotonic Regression（§4.3.2） |
| 10 | 3 | Fusion — 动态权重+MTF四框架投票（§4.3.3） |
| 11 | 6 | Risk — 六层硬约束+凯利+波动率锚定+黑天鹅+流动性+失效检测（§6） |
| 12 | 5 | Backtest — Walk-Forward引擎+前视偏差检测+成本模型+绩效指标（§4.6） |
| 13 | 4 | Pipeline + Signals — 事件驱动主循环+REST API+E2E测试（§7） |
