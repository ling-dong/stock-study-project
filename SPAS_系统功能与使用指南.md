# SPAS 系统功能与使用指南

**全称**：Sector Probability Analysis System（股市板块涨跌概率分析系统）

**版本**：V0.1

**定位**：基于 Al Brooks 价格行为理论的 A 股板块 ETF 涨跌概率分析系统，输出结构化的概率、风险回报比（RRR）和期望收益，为交易决策提供概率化参考。

---

## 目录

1. [系统概述](#1-系统概述)
2. [核心架构](#2-核心架构)
3. [完整功能模块](#3-完整功能模块)
4. [数据流与事件驱动](#4-数据流与事件驱动)
5. [配置系统](#5-配置系统)
6. [如何安装](#6-如何安装)
7. [如何使用](#7-如何使用)
8. [脚本参考](#8-脚本参考)
9. [API 接口](#9-api-接口)
10. [设计原则与约束](#10-设计原则与约束)

---

## 1. 系统概述

### 1.1 核心理念

SPAS 将 **Al Brooks 价格行为理论**（K线微观结构 + H2/L2/FB Setup + 多时间框架分析）与**统计概率框架**融合，针对 A 股板块 ETF 进行系统化的涨跌概率分析。

系统输出的是**概率化的决策参考信息**，而非绝对涨跌预测。交易员需结合系统输出与自身判断做最终决策。

### 1.2 支持的板块

| 板块ID   | 板块名称   | 代理ETF      | 成分股（部分）         |
|----------|------------|-------------|----------------------|
| 801010   | 农林牧渔   | 159825.SZ   | 牧原股份、温氏股份     |
| 801120   | 食品饮料   | 515170.SH   | 贵州茅台、五粮液      |
| 801180   | 医药生物   | 512010.SH   | 恒瑞医药、迈瑞医疗    |
| 801750   | 计算机     | 512720.SH   | 海康威视、科大讯飞    |
| 801770   | 通信       | 515880.SH   | 中国联通、中兴通讯    |
| 801760   | 半导体     | 512480.SH   | 中芯国际、北方华创    |
| 801730   | 电力       | 159611.SZ   | 长江电力、中国广核    |

板块配置在 `config/sectors.yaml` 中定义，新增板块仅需修改此文件。

### 1.3 预测期限

基于 13 只 ETF × 726 天历史 Walk-Forward 前向验证结果（2026-06-25）：

| 期限  | 胜率   | 平均收益  | 信号数 |
|-------|--------|----------|--------|
| 1天   | 44.9%  | -0.39%   | 34     |
| 3天   | 54.5%  | +0.25%   | 34     |
| **5天** | **52.6%** | **+0.53%** | **34** |
| 10天  | 41.7%  | +0.18%   | 34     |
| 20天  | 45.5%  | -0.31%   | 34     |

**最优预测期限**：5天（综合评分最高）

---

## 2. 核心架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    事件驱动总线（EventStream）                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ 数据层   │→│ 特征层   │→│ 预测层    │→│ 风险/信号层 │  │
│  │ §4.1    │  │ §4.2     │  │ §4.3     │  │ §6 / §7.3  │  │
│  └─────────┘  └──────────┘  └──────────┘  └────────────┘  │
│       │            │              │              │          │
│       ▼            ▼              ▼              ▼          │
│  多源数据      市场状态机      规则引擎       六层风控      │
│  主备切换      Setup识别       ML模型       凯利仓位      │
│  复权处理      一致性分析      概率校准      FastAPI      │
│                                                             │
│  辅助模块：情绪采集 ─ 板块关联 ─ 模型失效检测               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 处理流水线 

每根 K 线闭合后触发完整链路：

```
BarOHLCV → BarFeatureSvc(6维微观特征) → MarketStateSvc(状态机)
         → SetupRecogSvc(H2/L2/FB识别) → RuleEngine(规则概率)
         → MLModelLayer(LightGBM) → CalibrationLayer(Isotonic校准)
         → FusionLayer(规则+ML融合+MTF投票) → RiskConstraints(六层闸门)
         → 最终交易信号
```

---

## 3. 完整功能模块

### 3.1 数据层（src/data/）

#### 多源数据协调器 — `DataFetcher`
- **优先级机制**：本地 Parquet > Tushare Pro > AKShare（自动降级）
- **健康状态机**：连续3次失败自动切换数据源，30秒心跳检测
- **主备自动切换**：无需人工干预

#### 数据适配器
| 适配器 | 文件 | 优先级 | 说明 |
|--------|------|--------|------|
| LocalAdapter | `adapters/local.py` | 第一 | 本地 Parquet 缓存，零延迟 |
| TushareAdapter | `adapters/tushare.py` | 第二 | Tushare Pro API，支持日线/分钟线，ETF自动切换 fund_daily/daily 接口 |
| AKShareAdapter | `adapters/akshare.py` | 第三 | 备用数据源（待扩展） |

#### 价格复权 — `PriceAdjuster`
- 分钟级前复权：`P_adj = P_raw × factor_t / factor_base`
- 支持日级别复权因子表

#### 数据质量监控 — `DataQualityMonitor`
- 完整性检查：缺失率 < 5%
- 时效性检查：P99延迟 < 30秒
- 异常值检测：单Bar涨跌幅 > 10%、成交量 > 5倍均量

---

### 3.2 特征工程层（src/features/）

#### 3.2.1 K线微观结构 — `BarFeatureSvc`
**输出6维特征**（无状态纯计算，<1秒延迟）：

| 特征名 | 说明 | 计算公式 |
|--------|------|---------|
| body_ratio | 实体比例 | \|Close - Open\| / (High - Low) |
| close_position | 收盘价位置 | (Close - Low) / (High - Low) |
| upper_shadow | 上影线比例 | (High - max(O,C)) / (High - Low) |
| lower_shadow | 下影线比例 | (min(O,C) - Low) / (High - Low) |
| trend_bar | 趋势K线标识 | +1阳线 / -1阴线 / 0十字星 |
| limit_status | 涨跌停标记 | +1涨停 / -1跌停 / 0正常 |

#### 3.2.2 市场状态机 — `MarketStateSvc`
- **三态判定**：BULL / BEAR / NEUTRAL
- **三维指标**：EMA20斜率 + 趋势K线比例 + ADX(14)
- **延迟确认机制**：需连续2根Bar满足条件才切换，消除噪声干扰
- **置信度随持续时间递增**：初始0.3 → 最高0.9
- **Regime分类**：TRENDING(ADX>25) / VOLATILE(ADX 15-25) / RANGING(ADX<15)

#### 3.2.3 Setup识别 — `SetupRecogSvc`
**三种Setup类型**（Wyckoff框架）：

| Setup | 条件 | 适用场景 |
|-------|------|---------|
| **H2** | 上涨趋势中两腿回撤（Higher Low），第二腿缩量 → 放量突破确认 | 趋势回调买入 |
| **L2** | 下跌趋势中两腿反弹（Lower High），第二腿缩量 → 放量跌破确认 | 趋势反弹卖出 |
| **FB** | 关键位失败突破（False Breakout） | 反转交易 |

**状态机**：候选态(candidate) → 确认态(confirmed) → 失效态(invalidated)
- 候选态与确认态的区分是关键的前视偏差防护机制

**质量评分**（加权三维度）：
```
Quality = 0.35 × 回撤相似度 + 0.30 × 缩量程度 + 0.35 × 突破动量
```

#### 3.2.4 板块一致性 — `ConsensusSvc`
- **三指标**：上涨比例(up_ratio)、动量中位数(momentum_median)、龙头相关性(leader_corr)
- **Point-in-time权重**：按历史成分股权重计算，避免幸存者偏差
- **Stale降级**：数据延迟>5秒输出stale标记

---

### 3.3 预测决策层（src/prediction/）

#### 3.3.1 规则引擎 — `RuleEngine`（Layer 1）
- **触发条件**：每次 Setup 确认（100%事件）
- **延迟预算**：<50ms
- **输出**：结构化多维规则特征 + 先验概率 P_rule

特征向量：
```
{is_setup, setup_quality, historical_baserate, sample_size, 
 trend_aligned, market_state, market_confidence}
```

置信度判定：
| 条件 | 置信度 |
|------|--------|
| quality≥0.8 + 趋势对齐 + 市场趋势 | high |
| quality≥0.5 | medium |
| quality<0.5 | low（概率向0.5回归） |

#### 3.3.2 ML模型层 — `MLModelLayer`（Layer 2）
- **模型**：GradientBoostingClassifier（LightGBM为生产首选）
- **分Setup独立训练**：H2 / L2 / FB 各一个独立模型
- **强制特征选择**：每模型最多30个特征
- **触发条件**：规则置信度 < 0.85（约10%事件）
- **延迟预算**：P99 < 500ms

#### 3.3.3 概率校准层 — `CalibrationLayer`（Layer 3）
- **方法**：Isotonic Regression（保序校准）
- **重拟合周期**：60个交易日（月度）
- **ECE阈值**：>0.01 告警、>0.02 触发重训练、>0.05 暂停交易

#### 3.3.4 融合决策层 — `FusionLayer`
**规则-ML动态权重**：
```
w_rule = sigmoid(0.5×(1-n/500) + 0.5×(1-regime_similarity))
P_final = w_rule × P_rule + (1-w_rule) × P_ml
```

**多时间框架（MTF）投票权重**：
| 时间框架 | 权重 |
|---------|------|
| 日线 | 30% |
| 60分钟 | 30% |
| 15分钟 | 20% |
| 5分钟 | 20% |

**差异分析**：P_rule 与 P_ml 差异 > 10% 时输出差异报告

---

### 3.4 风控体系（src/risk/）

#### 3.4.1 六层硬约束 — `RiskConstraints`
| 层级 | 约束 | 阈值 | 动作 |
|------|------|------|------|
| L4 | 最大回撤 | -20% | **强制清仓**（最高优先级） |
| L3 | 月亏损 | -15% | **强制清仓** |
| L2 | 周亏损 | -8% | 仓位降50% |
| L1 | 日亏损 | -3% | 禁止新仓 |
| L5 | 单板块仓位 | 20% | 拒绝加仓 |
| L6 | 总仓位 | 80% | 拒绝加仓 |

#### 3.4.2 凯利公式 — `kelly_position`
```
f* = (p×b - q) / b
实际仓位 = 0.25 × f*   （1/4 Kelly，保守）
R:R < 1.0 → 不交易
```

#### 3.4.3 波动率锚定 — `VolatilityAnchor`
```
仓位 = 基础仓位 × (σ_normal / σ_current)^0.5
高波动(>1.5倍正常)：仓位降50%
极端波动(>90分位×2)：仓位上限5%
```

#### 3.4.4 尾部风险管理 — `TailRiskManager` + `CircuitBreaker`
| 触发条件 | 动作 |
|---------|------|
| VIX > 95%分位 或 板块单日跌 > 5% | 仓位降至10% |
| 跳空 > 3% | 清仓并暂停24小时 |
| 单日跌幅 > 7% | 熔断暂停该类Setup |
| 过去5天内有跌停 | 暂停交易（熔断记忆） |

#### 3.4.5 流动性监控 — `LiquidityMonitor`
- **Layer 1**：买卖价差异常（>3倍正常价差 → 拒绝）
- **Layer 2**：ETF折溢价（溢价>2%停止买入，折价>3%停止卖出）
- **Layer 3**：持仓流动性（持仓/日均成交量 > 5% → 拒绝）

#### 3.4.6 模型失效检测 — `FailureDetector`
六维检测：
| 维度 | 检测内容 | 触发条件 |
|------|---------|---------|
| D1 | 最大回撤 | > 15% |
| D2 | 胜率偏离 | 实际 vs 预测差异 > 15% |
| D3 | 波动率突破 | 当前/训练 > 2倍 |
| D4 | 相关性异常 | 板块间相关性 > 0.85 |
| D5 | 流动性恶化 | 价差比 > 3倍 |
| D6 | 置信度崩溃 | 概率方差 > 0.1 |

任一维度触发 → 建议暂停交易

---

### 3.5 回测体系（src/backtest/）

#### 3.5.1 Walk-Forward 回测引擎 — `WalkForwardBacktest`
- **训练窗口**：初始6个月
- **测试窗口**：每月滚动
- **最小样本**：1,000笔交易 / 5年以上数据

#### 3.5.2 绩效指标 — `BacktestMetrics`
- 胜率（Win Rate）
- 夏普比率（Sharpe Ratio）
- 最大回撤（Max Drawdown）
- Brier Score（概率校准度）
- 盈亏比（Profit Factor）

#### 3.5.3 交易成本模型 — `CostModel`
```
往返成本 = 佣金(0.25bps×2) + 印花税(1.0bps) + 滑点(0.5bps)
期望收益 = p_win×(收益-成本) - p_lose×(|止损|+成本) + p_flat×0
```
- 包含佣金、印花税、滑点、冲击成本
- 支持三态（win/lose/flat）期望收益计算

#### 3.5.4 前视偏差检测 — `ForwardBiasDetector`
```
偏差 = |Walk-Forward指标 - 全量指标| / |全量指标|
>30% → severe（严重）
>10% → moderate（中度）
<10% → clean（无偏差）
```

---

### 3.6 辅助模块

#### 3.6.1 情绪采集 — `SentimentCollector` + `SentimentCache`
- **四级优先级**：官方公告(0.4) > 主流财经(0.3) > 机构研报(0.2) > 社交媒体(0.1)
- **TTL**：30分钟缓存
- **时效衰减**：>24小时自动丢弃
- **非阻塞查询**：未命中返回中性值

#### 3.6.2 板块关联图 — `SectorLinkageGraph`
- **预定义产业链边**：最多80条（如 计算机→通信、食品→农业）
- **复杂度优化**：O(N²·T) → O(E·T)

#### 3.6.3 网络衰竭指数 — `ExhaustionIndex`
- 板块与关联板块同步衰竭比例
- 需连续3-5天确认才有效
- 不独立触发交易，仅作辅助参考

#### 3.6.4 事件总线 — `EventStream`
- **语义兼容**：Redis Streams API（XADD / XREADGROUP）
- **核心事件**：BAR_CLOSE → FEATURE_COMPUTE → STATE_TRANSITION → SETUP_DETECTED → PREDICTION → SIGNAL
- **异步非阻塞**：支持多消费者组订阅

---

### 3.7 数据模型（src/models/）

| 模型 | 文件 | 说明 |
|------|------|------|
| BarOHLCV | `bar.py` | K线数据，含OHLCV+可用时间+数据源 |
| FeatureVector | `feature.py` | 特征向量，不可变（frozen），含未来函数违规标记 |
| MarketState | `market_state.py` | 市场状态 BULL/BEAR/NEUTRAL，含置信度和持续时间 |
| SetupSignal | `setup_signal.py` | H2/L2/FB Setup信号，候选/确认/失效三态 |
| PredictionOutput | `prediction.py` | 预测输出，方向概率+RRR+期望收益+置信度 |
| BacktestRecord | `backtest.py` | 回测记录，入场/出场/盈亏/成本 |
| SectorConfig | `sector_config.py` | 板块配置，含point-in-time成分股权重 |
| SystemVersion | `version.py` | 四子版本：规则+模型+特征+数据，保证回测可复现 |

---

## 4. 数据流与事件驱动

### 4.1 事件类型

```
BAR_CLOSE → FEATURE_COMPUTE → STATE_TRANSITION → SETUP_DETECTED
         → CONSENSUS_UPDATE → PREDICTION_TRIGGER → PREDICTION
         → SENTIMENT_CACHED → SIGNAL
```

### 4.2 处理时序

```
[数据到达]
  ├── K线闭合 → BarFeatureSvc (<1s)
  ├── 状态更新 → MarketStateSvc (<500ms)（需连续2Bar确认）
  ├── Setup检测 → SetupRecogSvc (每Bar检测)
  ├── 一致性计算 → ConsensusSvc (<5s)
  ├── 规则推断 → RuleEngine (<50ms)（100%事件触发）
  ├── ML预测 → MLModelLayer (<500ms P99)（~10%事件触发）
  ├── 概率校准 → CalibrationLayer (<10ms)
  ├── 融合投票 → FusionLayer (<10ms)
  └── 风控闸门 → RiskConstraints (<10ms)
```

---

## 5. 配置系统

### 5.1 主配置文件：`config/settings.yaml`

关键配置项：

```yaml
# 数据源
tushare:
  token: "your_token"
  api_url: "https://ts.gyzcloud.top/api"

# 预测期限（基于前向验证优化）
prediction_horizon:
  optimal_days: 5         # 综合最优
  best_accuracy_days: 3   # 胜率最高

# 风控约束
risk_constraints:
  L1_daily_stop: -0.03
  L2_weekly_stop: -0.08
  L3_monthly_stop: -0.15
  L4_max_drawdown: -0.20
  L5_single_sector_pct: 0.20
  L6_total_exposure_pct: 0.80

# 市场状态（日线校准）
market_state:
  ema_period: 20
  trend_bar_ratio_bull: 0.45
  trend_bar_ratio_bear: 0.35
  adx_threshold: 20

# Setup识别（日线校准）
setup:
  volume_shrink_ratio: 0.92
  breakout_volume_multiplier: 1.05
  breakout_body_ratio: 0.30

# 概率校准
calibration:
  ece_threshold: 0.01
  ece_retrain: 0.02
  ece_freeze: 0.05
  refit_window_days: 60

# 交易成本
trading_costs:
  commission_bps: 0.25
  stamp_duty_bps: 1.0
  slippage_min_bps: 0.5
  slippage_max_bps: 1.5

# 模型监控
monitoring:
  psi_warning: 0.25
  psi_critical: 0.40
  winrate_deviation_warn: 0.15
  winrate_deviation_freeze: 0.25
```

### 5.2 板块配置：`config/sectors.yaml`

定义跟踪板块、ETF代码、成分股及关联关系。

---

## 6. 如何安装

### 6.1 环境要求

- Python ≥ 3.11
- 依赖：pandas, numpy, pydantic, PyYAML, lightgbm, scikit-learn, scipy, fastapi, uvicorn

### 6.2 安装步骤

```bash
# 1. 进入项目目录
cd D:\stock_market

# 2. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 Tushare Token（编辑 config/settings.yaml）
# 将 tushare.token 替换为你的 Tushare Pro token
```

---

## 7. 如何使用

### 7.1 快速开始（一键运行）

```bash
# 一键运行：获取数据 → 运行流水线 → 启动API服务
python scripts/start.py all
```

### 7.2 分步操作

#### Step 1: 获取真实数据

```bash
python scripts/start.py fetch
```

从 Tushare Pro 获取 13 只 ETF 的 3 年日线历史数据，保存为本地 Parquet 文件。

**注意**：如无 Tushare token，可先生成合成数据替代：
```bash
python scripts/generate_data.py
```

#### Step 2: 运行信号分析流水线

```bash
python scripts/start.py pipeline
```

加载本地数据 → 对所有标的运行完整流水线 → 输出每个标的的预测信号和风控评估。

#### Step 3: 运行回测验证

```bash
python scripts/start.py backtest
```

使用 Walk-Forward 框架对沪深300 ETF 进行历史回测，输出绩效报告（胜率、夏普、最大回撤、前视偏差检测）。

#### Step 4: 启动 API 服务

```bash
python scripts/start.py serve
```

启动 SPAS API 服务，访问 http://127.0.0.1:8000

> 也可使用 `python scripts/start_all.py` 一键启动 SPAS API + Investment Academy 后端 + Vue2 前端。

### 7.3 专项分析

#### 预测指定 ETF

```bash
python scripts/predict.py
```

对半导体ETF (512480) 和通信ETF (515880) 做完整的预测分析，包括：
- 市场状况（趋势/波动率）
- Setup 扫描（历史确认态和候选态）
- 5日预测（方向概率/目标达成率/止损率/RRR/期望收益）
- 凯利仓位计算
- 风控检查
- 对比总结和建议

#### 前向验证（找出最优预测期限）

```bash
python scripts/forward_validate.py
```

对 13 只 ETF 的所有历史 H2 信号做前向验证：在每个信号日后 1/3/5/10/20 天检查实际涨跌，统计各期限的胜率和平均收益，找出最优预测期限。

#### 全面验证

```bash
python scripts/verify.py
```

包含三个环节：
1. **数据校验**：检查13只ETF数据完整性+唯一性（防止Tushare重复返回）
2. **功能模块逐一测试**：全部9个核心模块功能验证
3. **电力ETF专项预测**：完整预测流程 + 历史信号回放

#### 诊断分析

```bash
python scripts/diagnose_power.py
```

针对电力ETF信号稀疏问题的深度诊断：走势分析、市场状态分布、候选态拒绝原因、与其它ETF对比。

---

## 8. 脚本参考

| 脚本 | 功能 |
|------|------|
| `scripts/start.py` | **主入口**，支持 fetch/pipeline/backtest/serve/all 五个子命令 |
| `scripts/fetch_real_data.py` | 从Tushare获取13只ETF的3年日线数据 |
| `scripts/generate_data.py` | 生成合成测试数据（6只ETF，500日线+2880根5分钟线） |
| `scripts/run_pipeline.py` | 加载数据 → 运行流水线 → 输出信号 + 风控评估 |
| `scripts/run_backtest.py` | Walk-Forward回测 + 绩效报告 + 前视偏差检测 |
| `scripts/predict.py` | 指定ETF完整预测分析（半导体+通信对比） |
| `scripts/verify.py` | 全面验证：数据校验 + 功能测试 + 单元测试 + 电力ETF预测 |
| `scripts/forward_validate.py` | 前向验证：找出最优预测期限 |
| `scripts/diagnose_power.py` | 电力ETF信号稀疏诊断 |

---

## 9. API 接口

启动服务后（`python scripts/start.py serve`），SPAS 核心 API 运行在 `http://127.0.0.1:8000`：

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/spas/system/status` | 系统状态 |
| GET | `/api/spas/signal/{code}` | 对指定 ETF 运行完整 SPAS 流水线 |
| GET | `/api/spas/market/etfs` | 可用 ETF 列表 |
| GET | `/api/spas/market/etfs/meta` | ETF 元数据概览 |
| GET | `/api/spas/market/etf/{code}/ohlcv` | ETF OHLCV 数据 |
| GET | `/system/status` | 兼容旧端点：系统状态 |
| GET | `/system/version` | 兼容旧端点：系统版本 |
| GET | `/signals/latest` | 兼容旧端点：最新信号（内存中） |
| GET | `/signals/history?limit=N` | 兼容旧端点：历史信号（内存中） |

### 信号响应字段

```json
{
  "symbol": "512480.SH",
  "timestamp": "2026-06-25T00:00:00",
  "current_price": 2.943,
  "market_state": {"state": "bull", "confidence": 0.9, "duration": 13},
  "setup_summary": {"confirmed_count": 44, "candidate_count": 71},
  "prediction": {
    "direction_prob": 0.5500,
    "target_prob": 0.3850,
    "stop_prob": 0.3600,
    "r_r_ratio": 2.00,
    "expected_value": 0.005300,
    "confidence_level": "medium",
    "setup_type": "H2"
  },
  "risk": {"kelly_position": 0.04, "risk_ok": true}
}
```

---

## 10. 设计原则与约束

### 10.1 前视偏差防护（四层机制）

1. **Model层**：FeatureVector 标注 computation_time，区分数据到达时间
2. **Setup层**：候选态(candidate) ≠ 确认态(confirmed)，后者需要后续Bar确认
3. **Backtest层**：ForwardBiasDetector 检测 Walk-Forward 与全量统计的差异
4. **Version层**：SystemVersion 四子版本确保完全可复现

### 10.2 关键约束

- **系统输出是概率参考**，不是交易指令
- **不直接执行交易**，交易决策由交易员完成
- **至少5年回测数据 + 1000笔交易**才能部署生产
- **所有胜率数字必须经过回测验证**，不使用任何文献中的未验证数字

### 10.3 延迟预算

| 环节 | 预算 |
|------|------|
| BarFeatureSvc | <1秒 |
| MarketStateSvc | <500ms |
| SetupRecogSvc | 实时 |
| RuleEngine (Layer 1) | <50ms |
| MLModelLayer (Layer 2) | <500ms (P99) |
| ConsensusSvc | <5秒 |
| 5分钟K线信号全链路 | <2秒 |
| 15分钟K线信号全链路 | <5秒 |

### 10.4 已知限制

- **信号稀疏性**：日线级别 H2 信号天然稀疏，低波动率板块（如电力）信号更少，这是设计预期行为
- **M/L2/FB Setup**：当前仅实现了 H2 的完整检测+确认逻辑，L2 和 FB 待后续扩展
- **AKShare适配器**：当前为占位实现，需要生产环境扩展
- **ML训练**：LightGBM为上产首选，当前使用 sklearn GradientBoosting 作为本地开发回退

---

## 附录：项目目录结构

```
D:\stock_market\
├── config/
│   ├── settings.yaml        # 全局配置（风控/模型/数据源/交易成本）
│   └── sectors.yaml         # 板块配置（8个板块+ETF+成分股）
├── src/
│   ├── models/              # Pydantic数据模型（8个模型）
│   │   ├── bar.py           # K线数据模型
│   │   ├── feature.py       # 特征向量（不可变）
│   │   ├── market_state.py  # 市场状态
│   │   ├── setup_signal.py  # Setup信号
│   │   ├── prediction.py    # 预测输出
│   │   ├── backtest.py      # 回测记录
│   │   ├── sector_config.py # 板块配置
│   │   └── version.py       # 系统版本
│   ├── data/                # 数据层
│   │   ├── fetcher.py       # 多源数据协调器
│   │   ├── quality.py       # 数据质量监控
│   │   ├── adjustment.py    # 分钟级复权处理
│   │   └── adapters/        # 数据适配器
│   │       ├── base.py      # 统一抽象接口
│   │       ├── local.py     # 本地Parquet适配器
│   │       ├── tushare.py   # Tushare Pro适配器
│   │       └── akshare.py   # AKShare适配器
│   ├── features/            # 特征工程层
│   │   ├── bar_feature.py   # K线微观结构特征(6维)
│   │   ├── market_state.py  # 市场状态机(EMA+ADX)
│   │   ├── setup_recog.py   # Setup识别(H2/L2/FB)
│   │   └── consensus.py     # 板块一致性指标
│   ├── prediction/          # 预测决策层
│   │   ├── rule_engine.py   # Layer 1: 规则引擎
│   │   ├── ml_model.py      # Layer 2: LightGBM预测
│   │   ├── calibration.py   # Layer 3: Isotonic校准
│   │   └── fusion.py        # 融合层+MTF投票
│   ├── risk/                # 风控体系
│   │   ├── constraints.py   # 六层硬约束+凯利公式
│   │   ├── volatility.py    # 波动率锚定仓位
│   │   ├── tail_risk.py     # 尾部风险+熔断
│   │   ├── liquidity.py     # 流动性监控
│   │   └── failure_detect.py # 模型失效检测
│   ├── backtest/            # 回测体系
│   │   ├── engine.py        # Walk-Forward回测引擎
│   │   ├── metrics.py       # 绩效指标(胜率/夏普/回撤/Brier)
│   │   ├── cost_model.py    # 交易成本模型
│   │   └── forward_bias.py  # 前视偏差检测
│   ├── pipeline/            # 主流水线
│   │   └── orchestrator.py  # 事件驱动全链路协调器
│   ├── signals/             # API服务
│   │   └── api.py           # FastAPI REST接口
│   ├── sentiment/           # 情绪分析
│   │   ├── collector.py     # 四级信息源采集
│   │   └── cache.py         # TTL缓存(30分钟)
│   ├── sector_linkage/      # 板块联动
│   │   ├── graph.py         # 产业链关联图
│   │   └── exhaustion.py    # 网络衰竭指数
│   ├── event_bus/           # 事件总线
│   │   ├── events.py        # 事件类型定义(9类)
│   │   └── stream.py        # Redis Streams语义实现
│   └── config/              # 配置加载
│       └── loader.py        # YAML → Pydantic配置
├── scripts/                 # 运行脚本(9个)
├── tests/                   # 测试(12个测试文件)
│   ├── unit/                # 单元测试(10个)
│   ├── integration/         # 集成测试(1个)
│   └── fixtures/            # 测试夹具
├── data/                    # 本地数据存储(Parquet)
├── pyproject.toml           # 项目配置
└── requirements.txt         # 依赖列表
```

---

> **文档生成日期**：2026-06-25
> **系统版本**：SPAS V0.1
> **基于**：全量源码扫描（42个源文件 + 9个脚本 + 2个配置文件）
