# Investment Academy — 投资学院学习系统设计规格

> 版本：V1.1 | 日期：2026-07-01 | 状态：设计中（新增P6交易心理与市场情绪）

## 1. 项目概述

### 1.1 目标

构建「投资学院」(Investment Academy)，一个基于 Streamlit 的交互式投资学习网站，帮助股市小白从零基础系统掌握投资和股市知识，最终成为投资大拿。

### 1.2 核心原则

- **与 SPAS 完全解耦**：两个系统独立演进，互不影响。投资学院不修改 SPAS 任何代码。
- **模块低耦合**：学院内部各模块边界清晰，单向依赖。
- **健壮可扩展**：内容作为数据驱动，新增章节无需改代码；Bridge 适配器隔离外部变化。

### 1.3 用户画像

- 股市完全新手
- 对投资感兴趣但缺乏系统学习路径
- 希望理论与实战结合
- 有编程基础（能理解代码示例）

---

## 2. 系统架构

### 2.1 系统边界

```
┌─────────────────────────────────────────────────────────┐
│                     D:\stock_market                      │
│                                                         │
│  ┌──────────────┐          ┌──────────────────────────┐ │
│  │  SPAS 系统    │          │  Investment Academy       │ │
│  │  (不改动)     │◄─────────│  (新系统)                 │ │
│  │              │  Bridge  │                          │ │
│  │ src/         │  适配器   │ investment_academy/      │ │
│  │ config/      │  单向依赖 │  ├── app.py              │ │
│  │ data/        │          │  ├── pages/              │ │
│  │ scripts/     │          │  ├── interactive/        │ │
│  │ tests/       │          │  ├── content/            │ │
│  └──────────────┘          │  ├── bridge/             │ │
│                             │  ├── models/            │ │
│                             │  └── tests/             │ │
│                             └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2.2 分层架构

```
┌────────────────────────────────────┐
│  Pages 层                          │  编排层：组合内容和交互组件
│  app.py, pages/*.py                │  不包含业务逻辑
├────────────────────────────────────┤
│  ↓                                │
│  Interactive 层 + Content 层       │  并行层：
│  interactive/*.py  content/*.{md,yaml}│  - Interactive：依赖于 Bridge
│                                    │  - Content：零依赖纯数据
├────────────────────────────────────┤
│  ↓                                │
│  Bridge 层                         │  适配器层：唯一 import SPAS 的地方
│  bridge/*.py                       │  对外暴露稳定接口
├────────────────────────────────────┤
│  ↓                                │
│  SPAS SDK (外部系统)                │  只读消费，零修改
└────────────────────────────────────┘
```

### 2.3 依赖规则

| 规则 | 说明 |
|------|------|
| `Pages → Interactive + Content` | 页面只做编排和路由 |
| `Interactive → Bridge` | 交互组件通过 Bridge 获取数据和算力 |
| `Bridge → SPAS` | **唯一的跨系统依赖**，单向只读 |
| `Content → ∅` | 纯数据，零依赖，可独立编写和复用 |
| `SPAS → ∅ (不知学院存在)` | SPAS 完全不受影响 |

### 2.4 目录结构

```
investment_academy/
├── pyproject.toml              # 独立依赖管理
├── requirements.txt            # 独立 requirements
├── app.py                      # Streamlit 入口 + 首页
├── pages/
│   ├── __init__.py
│   ├── knowledge/              # 知识轨道页面
│   │   ├── __init__.py
│   │   ├── p1_basics.py        # P1: 股市基础
│   │   ├── p2_technical.py     # P2: 技术分析入门
│   │   ├── p3_sectors.py       # P3: 板块与产业链
│   │   ├── p4_quant.py         # P4: 量化策略思维
│   │   ├── p5_risk.py          # P5: 风险管理
│   │   ├── p6_psychology.py    # P6: 交易心理与市场情绪
│   │   └── p7_integration.py   # P7: 实战整合
│   └── practice/               # 实践轨道页面
│       ├── __init__.py
│       ├── m1_data_lab.py      # M1: 数据勘探实验室
│       ├── m2_feature_lab.py   # M2: 特征工程实验室
│       ├── m3_prediction.py    # M3: 预测引擎探索
│       ├── m4_risk_sandbox.py  # M4: 风控沙盒
│       ├── m5_backtest.py      # M5: 回测分析器
│       └── m6_sentiment.py     # M6: 市场情绪实验室
├── interactive/                # 交互组件（可复用）
│   ├── __init__.py
│   ├── kline_chart.py          # K线图组件（Plotly）
│   ├── feature_explorer.py     # 特征参数调节器
│   ├── market_state_viz.py     # 市场状态可视化
│   ├── signal_viewer.py        # 信号标注查看器
│   ├── quiz_widget.py          # 测验组件
│   ├── sandbox_engine.py       # 交易沙盒引擎
│   ├── sentiment_viz.py        # 市场情绪可视化
│   ├── psychology_checklist.py # 交易心理自检清单
│   └── progress_dashboard.py   # 学习进度仪表盘
├── content/                    # 学习内容（纯数据）
│   ├── knowledge_track/
│   │   ├── p1_basics/
│   │   │   ├── chapter_01_stock_concept.md
│   │   │   ├── chapter_02_etf_basics.md
│   │   │   ├── chapter_03_a_share_rules.md
│   │   │   ├── chapter_04_kline_intro.md
│   │   │   ├── chapter_05_ohlcv.md
│   │   │   └── quiz.yaml
│   │   ├── p2_technical/
│   │   │   ├── chapter_01_trend.md
│   │   │   ├── chapter_02_microstructure.md
│   │   │   ├── chapter_03_ma_adx.md
│   │   │   ├── chapter_04_wyckoff_intro.md
│   │   │   ├── chapter_05_mtf_analysis.md
│   │   │   └── quiz.yaml
│   │   ├── p3_sectors/
│   │   │   ├── chapter_01_sector_classification.md
│   │   │   ├── chapter_02_industry_chain.md
│   │   │   ├── chapter_03_sector_rotation.md
│   │   │   ├── chapter_04_etf_as_proxy.md
│   │   │   └── quiz.yaml
│   │   ├── p4_quant/
│   │   │   ├── chapter_01_probability_thinking.md
│   │   │   ├── chapter_02_rule_strategy.md
│   │   │   ├── chapter_03_feature_engineering.md
│   │   │   ├── chapter_04_ml_in_trading.md
│   │   │   ├── chapter_05_mtf_fusion.md
│   │   │   └── quiz.yaml
│   │   ├── p5_risk/
│   │   │   ├── chapter_01_position_sizing.md
│   │   │   ├── chapter_02_drawdown_control.md
│   │   │   ├── chapter_03_volatility_adaptation.md
│   │   │   ├── chapter_04_tail_risk.md
│   │   │   ├── chapter_05_liquidity.md
│   │   │   └── quiz.yaml
│   │   ├── p6_psychology/
│   │   │   ├── chapter_01_self_awareness.md
│   │   │   ├── chapter_02_emotion_management.md
│   │   │   ├── chapter_03_cognitive_biases.md
│   │   │   ├── chapter_04_discipline_rules.md
│   │   │   ├── chapter_05_market_sentiment.md
│   │   │   ├── chapter_06_trading_journal.md
│   │   │   └── quiz.yaml
│   │   └── p7_integration/
│   │       ├── chapter_01_walk_forward.md
│   │       ├── chapter_02_forward_bias.md
│   │       ├── chapter_03_expected_value.md
│   │       ├── chapter_04_complete_system.md
│   │       └── quiz.yaml
│   └── practice_track/
│       ├── m1_data_lab/
│       │   ├── lab_guide.md
│       │   └── exercises.yaml
│       ├── m2_feature_lab/
│       │   ├── lab_guide.md
│       │   └── exercises.yaml
│       ├── m3_prediction/
│       │   ├── lab_guide.md
│       │   └── exercises.yaml
│       ├── m4_risk_sandbox/
│       │   ├── lab_guide.md
│       │   └── exercises.yaml
│       ├── m5_backtest/
│       │   ├── lab_guide.md
│       │   └── exercises.yaml
│       └── m6_sentiment/
│           ├── lab_guide.md
│           └── exercises.yaml
├── bridge/                     # SPAS 适配器层
│   ├── __init__.py
│   ├── data_reader.py          # 读取 ETF 数据（Parquet）
│   ├── knowledge_extractor.py  # 提取公式、参数、概念
│   └── compute_runner.py       # 运行 SPAS 计算
├── models/                     # 学院数据模型
│   ├── __init__.py
│   ├── progress.py             # 学习进度模型
│   ├── quiz.py                 # 测验结果模型
│   └── user.py                 # 用户偏好模型
├── db/                         # 本地数据库
│   ├── __init__.py
│   ├── schema.sql              # SQLite schema
│   └── repository.py           # 数据访问层
└── tests/
    ├── __init__.py
    ├── test_content/
    │   └── test_quiz_parsing.py
    ├── test_bridge/
    │   ├── test_data_reader.py
    │   └── test_knowledge_extractor.py
    ├── test_interactive/
    │   └── test_sandbox_engine.py
    └── test_models/
        └── test_progress.py
```

---

## 3. 学习内容体系

### 3.1 知识轨道（Knowledge Track）

按投资概念组织，从零基础到系统掌握。

#### P1: 股市基础（5章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 1.1 | 什么是股票？ | 股票本质、股东权益、一级/二级市场 | — |
| 1.2 | ETF 入门 | ETF 概念、行业ETF、ETF vs 个股 | `sectors.yaml` ETF 列表 |
| 1.3 | A股交易规则 | T+1制度、涨跌停板、交易时间、手续费 | `limit_status` 特征、Tushare适配器 |
| 1.4 | K线图入门 | 蜡烛图结构、OHLCV含义、时间框架 | `BarOHLCV` 数据模型 |
| 1.5 | 基本术语 | 成交量、市值、换手率、PE/PB | `config/settings.yaml` |

#### P2: 技术分析入门（5章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 2.1 | 趋势判断 | 牛市/熊市/震荡、趋势线、道氏理论 | `MarketState` BULL/BEAR/NEUTRAL |
| 2.2 | K线微观结构 | 实体比、影线、收盘位置、趋势棒 | `BarFeatureSvc` 6维特征公式 |
| 2.3 | 均线与ADX | EMA计算、ADX含义、趋势强度 | `MarketStateSvc` EMA(20)、ADX(14) |
| 2.4 | Wyckoff理论入门 | 供需法则、积累/派发、H2/L2模式 | `SetupRecogSvc` H2/L2/FB |
| 2.5 | 多时间框架分析 | MTF原理、各框架权重、背离分析 | `FusionLayer` 4框架投票 |

#### P3: 板块与产业链（4章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 3.1 | 行业分类体系 | 申万/中信分类、行业划分逻辑 | `sectors.yaml` 14行业 |
| 3.2 | 产业链分析 | 上下游关系、传导效应 | `graph.py` 60+产业链边 |
| 3.3 | 板块轮动 | 轮动逻辑、先行/滞后行业 | 耗尽指数 `exhaustion.py` |
| 3.4 | ETF 实战 | 板块ETF选择、ETF溢价/折价 | ETF数据、流动性监控 |

#### P4: 量化策略思维（5章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 4.1 | 概率思维 | 概率vs预测、基率、贝叶斯更新 | `rule_engine.py` 基率、收缩估计 |
| 4.2 | 规则策略设计 | 条件组合、质量评分、趋势对齐 | `RuleEngine` 8维规则向量 |
| 4.3 | 特征工程 | 特征构造、选择、时点标注 | `bar_feature.py`、`FeatureVector` |
| 4.4 | ML 在投资中的应用 | GBClassifier、校准、ECE | `ml_model.py`、`calibration.py` |
| 4.5 | 融合决策 | 动态权重、投票融合、分歧处理 | `FusionLayer` sigmoid权重 |

#### P5: 风险管理（5章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 5.1 | 仓位管理 | Kelly公式、fractional Kelly、R:R比 | `constraints.py` 0.25 Kelly |
| 5.2 | 回撤控制 | 最大回撤、分层止损、连续亏损 | 6层硬约束、5连亏暂停 |
| 5.3 | 波动率适应 | 波动率锚定、仓位缩放 | `volatility.py` sigma缩放 |
| 5.4 | 尾部风险 | VIX、跳空、熔断 | `tail_risk.py` 暴跌检测 |
| 5.5 | 流动性管理 | 价差、溢价/折价、容量限制 | `liquidity.py` 3层检查 |

#### P6: 交易心理与市场情绪（6章）

> 🧠 职业交易员共识：技术分析占20%，心理占60%，风控占20%。这是从"知道"到"做到"的关键跨越。

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 6.1 | 交易者的自我认知 | 风险偏好评估、性格与交易风格、了解自己的心理弱点、制定个人交易信条 | — (纯心理学) |
| 6.2 | 情绪识别与管理 | 贪婪(FOMO追高)、恐惧(恐慌割肉)、过度自信(连续盈利后)、报复交易(亏损后加倍)、焦虑(持仓不安)、Tilt状态识别 | — |
| 6.3 | 认知偏差 | 确认偏差(只看支持自己的信息)、锚定效应(被买入价锁定)、损失厌恶(不愿止损)、近因偏差(过度重视最近事件)、幸存者偏差(只看到成功的)、过度交易偏差 | — |
| 6.4 | 纪律与交易规则 | 交易前Checklist、何时绝对不能交易(情绪化/疲劳/连续亏损)、交易计划制定、规则遵守与自我监督 | — |
| 6.5 | 市场情绪判断 | 恐惧贪婪指数(VIX/FGI)、成交量与情绪关系、极端情绪作为反向指标、新闻舆论情绪分析、机构vs散户情绪背离 | `sentiment/collector.py` 4层优先级、43行业关键词 |
| 6.6 | 交易日志与复盘 | 每笔交易记录什么、如何做周/月复盘、从错误中学习、建立个人错误模式库、持续改进循环 | — |

#### P7: 实战整合（4章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 7.1 | Walk-Forward 回测 | 滚动窗口、训练/测试分离 | `engine.py` 6月训练+1月测试 |
| 7.2 | 前视偏差 | 偏差检测、严重程度分级 | `forward_bias.py` >30%严重 |
| 7.3 | 期望值计算 | 含成本期望值、Brier分数 | `cost_model.py`、`metrics.py` |
| 7.4 | 完整交易系统 | 数据→特征→预测→风控→心理→执行→评估 | 完整 Pipeline + 心理自检 |

### 3.2 实践轨道（Practice Track）

按 SPAS 模块组织，动手实验。

| 模块 | 名称 | 核心实验 | 交互组件 |
|------|------|----------|----------|
| M1 | 数据勘探实验室 | 浏览14个ETF的K线数据、对比走势、认识数据质量问题 | `data_explorer.py` |
| M2 | 特征工程实验室 | 调节参数看K线特征、观察市场状态切换、识别H2/L2形态 | `feature_explorer.py` |
| M3 | 预测引擎探索 | 查看规则引擎输出、对比ML预测、观察概率校准 | `signal_viewer.py` |
| M4 | 风控沙盒 | 模拟仓位计算、调节Kelly参数、触发止损场景 | `sandbox_engine.py` |
| M5 | 回测分析器 | 查看回测报告、理解Sharpe/MDD/PF等指标 | 回测结果可视化 |
| M6 | 市场情绪实验室 | 查看SPAS情绪数据、行业关键词分析、情绪与走势对比、恐惧贪婪指数模拟 | `sentiment_viz.py` |

---

## 4. 交互功能设计

### 4.1 测验系统

- **类型**：单选、多选、判断
- **时机**：每章末尾
- **反馈**：即时判分 + 解析
- **数据**：`content/**/quiz.yaml` 定义题库
- **存储**：SQLite 记录成绩历史

### 4.2 数据探索器

- **功能**：选ETF → 选时间范围 → 看K线图 → 叠加信号标注
- **数据源**：Bridge → Parquet 文件
- **图表**：Plotly OHLC 图 + 成交量柱状图 + 信号标记
- **参数**：时间框架切换（日线/60分钟/15分钟）

### 4.3 特征实验室

- **功能**：查看6维K线特征 → 调节阈值 → 观察特征变化
- **参数调节**：ADX阈值、BULL趋势比率、Volume收缩率、Body比率
- **实时反馈**：特征值变化 + 状态机转换可视化

### 4.4 交易沙盒

- **功能**：选择历史时间段 → 接收信号 → 做出买卖决策 → 看到结果
- **规则**：模拟T+1、涨跌停、交易成本
- **指标**：累计收益、胜率、最大回撤、Sharpe
- **目标**：在无风险环境中积累决策经验

### 4.5 市场情绪可视化

- **功能**：展示SPAS情绪数据的走势图 → 对比ETF价格走势 → 观察情绪与价格的关系
- **数据源**：Bridge → SPAS `sentiment/collector.py` 的历史情绪数据（如有），否则用成交量+价格构建简易情绪指标
- **展示**：行业情绪热力图、情绪-价格叠加图、极端情绪标注
- **学习目标**：理解"别人贪婪时恐惧，别人恐惧时贪婪"的量化表达

### 4.6 交易心理自检清单

- **功能**：每次学习前/沙盒交易前，弹出心理状态自查清单
- **题目示例**：
  - "我今天是否处于强烈的某种情绪中（愤怒/焦虑/过度兴奋）？"
  - "我上一次交易是盈利还是亏损？是否可能影响我的判断？"
  - "我是否因为FOMO想交易，而不是基于规则？"
  - "今天的市场环境是否适合我的策略？"
- **反馈**：综合评分 + 风险等级（🟢 适合交易 / 🟡 谨慎 / 🔴 建议暂停）
- **存储**：SQLite 记录心理状态历史，可回顾"我在什么心理状态下交易表现最好"

### 4.7 学习进度仪表盘

- **数据**：已读章节、测验成绩、实验完成状态、活跃天数、心理自检记录
- **展示**：进度条、成绩趋势图、徽章成就
- **存储**：SQLite 本地持久化

---

## 5. 数据模型

### 5.1 学习进度 (LearningProgress)

```python
class ChapterProgress:
    chapter_id: str       # e.g. "p1_ch1"
    completed: bool
    quiz_score: float     # 0-1
    quiz_attempts: int
    last_accessed: datetime
    time_spent_seconds: int

class LabProgress:
    lab_id: str           # e.g. "m1"
    completed: bool
    exercises_done: list[str]
    last_accessed: datetime
```

### 5.2 测验 (Quiz)

```yaml
# content/knowledge_track/p1_basics/quiz.yaml
chapter: p1_ch1
questions:
  - id: q1
    type: single_choice
    question: "股票代表的是什么？"
    options:
      - "公司债务"
      - "公司所有权的一部分"
      - "政府债券"
      - "银行存款凭证"
    answer: 1  # index
    explanation: "股票是股份公司发行的所有权凭证..."
```

### 5.3 交易心理记录 (PsychologyRecord)

```python
class PsychologyCheckRecord:
    timestamp: datetime
    checklist_scores: dict[str, int]  # 每题的1-5评分
    overall_risk_level: str           # "green" | "yellow" | "red"
    proceeded_to_trade: bool          # 是否仍然进行了交易
    self_notes: str                   # 自由记录

class TradingJournalEntry:
    date: datetime
    setup_type: str            # H2 / L2 / FB / 其他
    entry_reason: str          # 入场理由
    exit_reason: str           # 出场理由
    pnl_pct: float             # 收益率
    emotional_state: str       # 交易时情绪状态
    lesson_learned: str        # 学到的教训
    mistake_flag: bool         # 是否标记为错误交易
```

### 5.4 用户偏好 (UserPreferences)

```python
class UserPreferences:
    current_phase: str          # 当前学习阶段
    preferred_timeframe: str    # 偏好时间框架
    sandbox_balance: float      # 沙盒虚拟资金
    achievements: list[str]     # 已解锁成就
    risk_profile: str           # 风险偏好评估结果: "conservative" | "moderate" | "aggressive"
```

---

## 6. 技术栈

| 层 | 技术选型 | 版本 | 用途 |
|----|---------|------|------|
| 前端框架 | Streamlit | ≥1.28 | 页面渲染、导航 |
| 图表 | Plotly | ≥5.17 | K线图、指标图 |
| 数据处理 | Pandas | ≥2.0 | 数据分析 |
| 配置解析 | PyYAML | ≥6.0 | 内容文件解析 |
| 数据库 | SQLite3 | 内置 | 进度持久化 |
| 测试 | Pytest | ≥7.0 | 独立测试 |
| SPAS SDK | SPAS (本地) | ≥0.1.0 | 数据与算力 |

---

## 7. 关键设计决策

### 7.1 为什么是 Streamlit 而不是 Web 框架？

- 纯 Python，与 SPAS 技术栈一致
- 本地使用场景不需要前后端分离
- 内置 Widget 和图表支持
- 开发速度远超 FastAPI + React

### 7.2 Bridge 层为什么不直接 import SPAS 各处？

- 集中管理跨系统依赖，SPAS API 变化时只需修改 Bridge
- 对外提供稳定的、语义化的接口（隐藏 SPAS 内部复杂度）
- 可 Mock 进行独立测试

### 7.3 内容为什么用 Markdown 而不是数据库？

- Markdown 可版本管理（git diff 友好）
- 非技术人员也能编辑内容
- 内容与代码完全解耦
- 可被任何 Markdown 渲染器消费

---

## 8. 非功能需求

| 类别 | 要求 |
|------|------|
| 性能 | 页面加载 < 2s，图表渲染 < 1s |
| 可靠性 | Bridge 层异常不影响学院主流程 |
| 可维护性 | 新增章节只需加 Markdown + Quiz YAML |
| 可测试性 | 每层独立可测，Bridge 层可 Mock |
| 健壮性 | SPAS 不可用时学院仍可浏览已有内容 |

---

## 9. 实施策略

### Phase 1: 骨架搭建（优先）

1. 创建 `investment_academy/` 目录结构
2. 配置独立 `pyproject.toml`
3. 搭建 Streamlit 入口 `app.py` + 首页
4. 实现 Bridge 层（data_reader + knowledge_extractor）
5. 实现数据模型 + SQLite schema

### Phase 2: 内容填充

6. 编写 P1 5章 Markdown + 测验
7. 实现测验组件
8. 逐步完成 P2-P6（可分批交付）

### Phase 3: 交互组件

9. K线图组件
10. 特征实验室
11. 交易沙盒

### Phase 4: 完善

12. 学习进度仪表盘
13. 术语表
14. 测试覆盖

---

## 10. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| SPAS API 变更导致 Bridge 失效 | Bridge 层隔离 + 版本锁定 |
| Streamlit 性能瓶颈 | 图表数据预聚合，避免实时重计算 |
| 内容编写工作量大 | 分批交付，先完成 P1-P2 验证可行性 |
| 用户失去学习动力 | 沙盒游戏化 + 成就系统保持参与度 |

---

## 附录 A: SPAS 知识资产清单

见探索报告。核心资产：
- 6维K线特征公式
- 3状态市场机 + ADX趋势分类
- Wyckoff H2/L2/FB 模式识别
- 8维规则向量 + LightGBM + Isotonic校准
- 6层风控 + Kelly + 波动率锚定
- Walk-Forward回测 + 前视偏差检测
- 60+产业链边 + 情绪分析
- 13 ETF × 726天实证回测数据
