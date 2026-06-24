# SPAS 实现设计规格

**日期**：2026-06-24
**状态**：已确认
**设计文档基准**：`sector_probability_system.agent.final.md`（V1.0，2026-06-23修订版）

---

## 1. 实现策略

**方案 A：模块化单体架构** — 将所有"微服务"实现为同一 Python 进程内的独立模块，通过内部事件总线通信。模块接口与设计文档 §3.2 定义的微服务一一对应，后续拆分为独立容器时零接口变更。

## 2. 技术栈

- Python 3.11+, pandas, numpy, Pydantic v2, asyncio
- LightGBM（ML模型）, scikit-learn（校准/评估）
- pytest（测试）, YAML（配置）, FastAPI（REST API）

## 3. 项目结构

```
stock_market/
├── config/
│   ├── settings.yaml
│   └── sectors.yaml
├── src/
│   ├── models/           # §5 数据模型（Pydantic v2, 8个模型）
│   ├── data/             # §4.1 数据采集层（3个适配器 + 协调器）
│   ├── features/         # §4.2 特征计算层（4个模块）
│   ├── prediction/       # §4.3 预测模型层（3层 + 融合）
│   ├── sentiment/        # §4.4 文本情绪模块
│   ├── sector_linkage/   # §4.5 板块关联模块
│   ├── risk/             # §6 风控体系（6个子模块）
│   ├── backtest/         # §4.6 回测引擎
│   ├── event_bus/        # §7.1 事件总线（Redis Streams语义）
│   ├── signals/          # §7.3 信号输出
│   ├── config/loader.py  # 配置管理
│   └── pipeline/         # 流水线编排
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## 4. 数据模型（对应设计文档 §5）

| 模型类 | 设计文档表 | 关键约束 |
|--------|----------|---------|
| `BarOHLCV` | bar_ohlcv | data_availability_time >= timestamp |
| `FeatureVector` | feature_vector | future_function_violation标记 |
| `MarketState` | market_state | state∈{bull,bear,neutral}, confidence∈[0,1] |
| `SetupSignal` | setup_signal | candidate/confirmed状态机 |
| `PredictionOutput` | prediction_output | Isotonic校准后概率, 三态期望收益 |
| `BacktestRecord` | backtest_record | 四元组version_id, 逐笔成本明细 |
| `SectorConfig` | sector_config | point-in-time历史权重 |
| `SystemVersion` | system_version | {rules, model, features, data}四子版本 |

## 5. 核心算法

### 特征工程
- **BarFeatureSvc**: body_ratio, close_position, upper/lower_shadow, trend_bar, limit_status（6维）
- **MarketStateSvc**: EMA20斜率+趋势K线比例+ADX>25，连续2Bar确认，confidence随duration递增
- **SetupRecogSvc**: H2/L2/FB候选态→确认态状态机，3维度综合质量评分[0,1]
- **ConsensusSvc**: up_ratio, momentum_median, leader_corr, stale降级

### 预测模型（3层）
- Layer 1: 规则引擎（P99<50ms）→ {is_setup, setup_quality, historical_baserate, sample_size}
- Layer 2: LightGBM+Transformer（P99<500ms, 仅confidence<0.85触发）
- Layer 3: Isotonic Regression校准（ECE<0.01）

### 融合
- 规则+ML动态权重: w_rule = sigmoid(0.5*(1-n/500) + 0.5*(1-regime_sim))
- MTF四框架投票: 日线30% + 60分钟30% + 15分钟20% + 5分钟20%

### 风控
- 六层硬约束执行序: L4>L3>L2>L1>L5>L6
- 凯利: position ≤ 0.25*f*
- 波动率锚定: position *= (σ_normal/σ_current)^0.5

## 6. 实现批次（13批，按数据依赖关系）

| 批次 | 模块 | 可并行测试 |
|------|------|-----------|
| 1 | models/ 全部8个数据模型 | 单元测试 |
| 2 | event_bus/ + config/ | 单元测试 |
| 3 | data/adapters/* + fetcher | mock数据测试 |
| 4 | features/bar_feature | 合成K线测试 |
| 5 | features/market_state | 序列数据测试 |
| 6 | features/setup_recog | 模式匹配测试 |
| 7 | features/consensus | 板块数据测试 |
| 8 | prediction/rule_engine | 规则验证测试 |
| 9 | prediction/ml_model + calibration | mock训练测试 |
| 10 | prediction/fusion | 融合逻辑测试 |
| 11 | risk/* | 边界条件测试 |
| 12 | backtest/* | Walk-Forward测试 |
| 13 | signals/* + pipeline/* | 端到端测试 |

## 7. 每批次验证标准
- 单元测试覆盖率 > 85%
- 关键算法与设计文档公式对照验证
- 前一批次回归测试全部通过
- 数据模型字段约束满足设计文档 §5 定义
