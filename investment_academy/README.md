# 投资学院 Investment Academy

> 基于 Vue2 + FastAPI 的交互式投资学习系统 · 从零基础到投资大拿

---

## 1. 项目概述

### 1.1 这是什么？

「投资学院」是一个本地运行的交互式投资学习网站。它将 SPAS（Sector Probability Analysis System）项目中沉淀的投资知识、真实市场数据和量化分析方法，转化为一套**系统化的学习课程**——从最基础的「什么是股票」到「完整交易系统搭建」。

### 1.2 核心理念

- **理论 + 实战双轨并行**：知识轨道学概念，实践轨道动手做
- **用真实数据学习**：不是抽象的教学案例，而是真实的 A 股 ETF 数据
- **SPAS 核心单一可信源**：预测、市场数据、风控均由 SPAS 核心 API 提供，学院不自行实现
- **零基础友好**：从最基本的概念开始，逐步深入

### 1.3 启动方式（推荐）

```bash
cd D:\stock_market
python scripts/start_all.py
```

该脚本会同时启动：
- SPAS Core API — http://127.0.0.1:8000
- Investment Academy Backend — http://127.0.0.1:8001
- Vue2 Frontend — http://127.0.0.1:8080

浏览器打开 http://localhost:8080 开始学习。

### 1.4 备选启动方式

**手动启动（三个终端）：**

```bash
# 终端 1: SPAS Core API
cd D:\stock_market
python scripts/start.py serve

# 终端 2: Academy Backend
cd D:\stock_market\investment_academy
uvicorn backend.main:app --host 127.0.0.1 --port 8001

# 终端 3: Vue2 Frontend
cd D:\stock_market\investment_academy\frontend
npm install
npm run serve
```

**一键关闭：**

```bash
cd D:\stock_market
python scripts/stop_all.py
```

---

## 2. 系统架构

### 2.1 与 SPAS 的关系

```
D:\stock_market
│
├── SPAS 核心系统 (src/)
│   ├── 数据/特征/预测/风控/回测
│   └── FastAPI 服务: http://127.0.0.1:8000
│          ▲
│          │ HTTP /api/spas/*
│          │
├── Investment Academy (investment_academy/)
│   ├── backend/          FastAPI 后端 (port 8001)
│   │   └── routers/spas.py  → 代理到 SPAS Core API
│   ├── frontend/         Vue2 SPA (port 8080)
│   ├── core/             共享库（models/db/bridge/engine）
│   └── content/          学习内容（Markdown/YAML）
```

> 投资学院**不自行实现预测算法**。所有涨跌概率、Setup 识别、风控计算均由 SPAS 核心 API 提供；学院后端 `/api/spas/*` 仅做代理，便于统一 CORS 和入口管理。

### 2.2 分层架构

```
Vue2 前端
   │
   ├── /api/spas/*     → SPAS Core API (port 8000)  [预测/市场数据]
   └── /api/*          → Academy Backend (port 8001) [学习/进度/沙盒/用户]

Academy Backend
   │
   ├── routers/spas.py        → 代理 SPAS Core API
   ├── routers/manual_analysis.py → 手动指标合成（独立功能，非 SPAS 核心）
   ├── routers/content.py     → 学习内容
   ├── routers/quiz.py        → 测验
   ├── routers/progress.py    → 学习进度
   ├── routers/sandbox.py     → 交易沙盒
   ├── routers/user.py        → 用户偏好/心理/日志
   └── routers/market.py      → 市场数据（可逐步迁移到 SPAS API）

Academy Core (shared library)
   │
   ├── models/    数据模型
   ├── db/        SQLite 持久化
   ├── bridge/    SPAS 数据读取适配器
   └── engine/    内容加载/沙盒引擎
```

### 2.3 依赖规则

| 规则 | 说明 |
|------|------|
| `Frontend → SPAS Core API` | 预测、市场数据、OHLCV 直接由 SPAS 提供 |
| `Frontend → Academy Backend` | 学习、进度、沙盒、测验、用户功能 |
| `Academy Backend → SPAS Core API` | `/api/spas/*` 代理，不实现预测算法 |
| `Academy Core → SPAS (只读)` | Bridge 读取 Parquet/配置，不写入 SPAS |
| `Content → ∅` | 纯数据，零依赖 |

### 2.4 目录结构

```
investment_academy/
├── README.md                     # 本文档
├── pyproject.toml                # 独立依赖管理
├── requirements.txt              # pip install 用
├── 使用指南.md                    # 详细操作指南
│
├── core/                         # 共享核心库（Backend 与前端共用）
│   ├── models/                   # 数据模型（dataclass）
│   ├── db/                       # SQLite 持久化（6 表 + CRUD）
│   ├── bridge/                   # SPAS 数据读取适配器
│   └── engine/                   # 内容加载 + 沙盒引擎
│
├── backend/                      # FastAPI 后端
│   ├── main.py                   # 入口 + CORS
│   ├── schemas.py                # Pydantic 模型
│   └── routers/                  # 路由模块
│       ├── content.py            # 学习内容
│       ├── quiz.py               # 测验
│       ├── progress.py           # 学习进度
│       ├── market.py             # 市场数据
│       ├── sandbox.py            # 交易沙盒
│       ├── user.py               # 用户偏好/心理/日志
│       ├── knowledge.py          # 投资知识
│       ├── spas.py               # 代理 SPAS Core API
│       └── manual_analysis.py    # 手动指标合成（独立功能）
│
├── frontend/                     # Vue2 SPA
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   ├── components/           # KLineChart / QuizWidget / MarkdownViewer
│   │   └── api/                  # axios 封装
│   └── vue.config.js             # 开发代理: /api/spas → 8000, /api → 8001
│
├── content/                      # 学习内容（7 阶段 34 章 + 170+ 测验题）
│   ├── knowledge_track/
│   │   ├── p1_basics/ ... p7_integration/
│   └── practice_track/
│       └── m1_data_lab/
│
└── tests/                        # 测试套件（60 个测试）
    ├── test_models/
    ├── test_db/
    ├── test_bridge/
    ├── test_content/
    └── test_backend/
```

---

## 3. 学习内容体系

### 3.1 知识轨道（Knowledge Track）

按投资概念组织，从零基础到系统掌握，共 **7 个阶段 / 34 章**。

```
P1(5章) → P2(5章) → P3(4章) → P4(5章) → P5(5章) → P6(6章) → P7(4章)
```

#### P1: 股市基础（5章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 | 状态 |
|------|------|-----------|-------------|------|
| 1.1 | 什么是股票？ | 股票本质、股东权益、一级/二级市场 | — | ✅ |
| 1.2 | ETF 入门 | ETF 概念、行业ETF、ETF vs 个股 | `sectors.yaml` ETF 列表 | 📝 |
| 1.3 | A股交易规则 | T+1制度、涨跌停板、交易时间 | `limit_status` 特征 | 📝 |
| 1.4 | K线图入门 | 蜡烛图结构、OHLCV含义、时间框架 | `BarOHLCV` 数据模型 | 📝 |
| 1.5 | 基本术语 | 成交量、市值、换手率、PE/PB | `config/settings.yaml` | 📝 |

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

> 🧠 职业交易员共识：技术分析占20%，心理占60%，风控占20%。

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 6.1 | 交易者的自我认知 | 风险偏好评估、性格与交易风格 | — |
| 6.2 | 情绪识别与管理 | 贪婪(FOMO)、恐惧(恐慌)、报复交易、Tilt状态 | — |
| 6.3 | 认知偏差 | 确认偏差、锚定效应、损失厌恶、近因偏差 | — |
| 6.4 | 纪律与交易规则 | 交易前Checklist、何时绝对不能交易 | — |
| 6.5 | 市场情绪判断 | 恐惧贪婪指数、极端情绪反向指标 | `sentiment/collector.py` |
| 6.6 | 交易日志与复盘 | 每笔交易记录、周/月复盘、错误模式库 | — |

#### P7: 实战整合（4章）

| 章节 | 标题 | 核心知识点 | SPAS 知识来源 |
|------|------|-----------|-------------|
| 7.1 | Walk-Forward 回测 | 滚动窗口、训练/测试分离 | `engine.py` 6月训练+1月测试 |
| 7.2 | 前视偏差 | 偏差检测、严重程度分级 | `forward_bias.py` |
| 7.3 | 期望值计算 | 含成本期望值、Brier分数 | `cost_model.py`、`metrics.py` |
| 7.4 | 完整交易系统 | 数据→特征→预测→风控→心理→执行→评估 | 完整 Pipeline |

### 3.2 实践轨道（Practice Track）

按 SPAS 模块组织，动手实验，共 **6 个实验室**。

| 模块 | 名称 | 核心实验 | 交互组件 | 状态 |
|------|------|----------|----------|------|
| M1 | 数据勘探实验室 | 浏览ETF数据、对比走势、认识数据质量 | `data_explorer.py` | ✅ |
| M2 | 特征工程实验室 | 调节参数看特征变化、识别H2/L2形态 | `feature_explorer.py` | 📝 |
| M3 | 预测引擎探索 | 查看规则输出、对比ML预测 | `signal_viewer.py` | 📝 |
| M4 | 风控沙盒 | 模拟仓位计算、触发止损场景 | `sandbox_engine.py` | 📝 |
| M5 | 回测分析器 | 查看回测报告、理解指标 | 回测结果可视化 | 📝 |
| M6 | 市场情绪实验室 | 情绪数据、行业对比、恐惧贪婪指数 | `sentiment_viz.py` | 📝 |

---

## 4. 交互功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 📝 **测验系统** | 单选/多选/判断，即时判分 + 解析，SQLite 记录 | ✅ |
| 📊 **ETF 数据探索器** | 选 ETF → 看 K 线图 → 叠加信号标注 | ✅ 基础版 |
| 🔬 **特征实验室** | 调节参数观察特征变化 + 状态机可视化 | 📝 |
| 🎮 **交易沙盒** | ETF选择 → 逐日OHLCV → 买卖决策 → 绩效报告 | ✅ |
| 💬 **市场情绪可视化** | 情绪热力图、情绪-价格叠加图 | 📝 |
| 🧠 **交易心理自检清单** | 心理问卷 → 风险等级（🟢🟡🔴） | 📝 |
| 📊 **学习进度仪表盘** | 进度条、成绩趋势、徽章成就 | 📝 |

---

## 5. 数据模型

### 5.1 学习进度 (LearningProgress)

```python
class ChapterProgress:
    chapter_id: str       # e.g. "p1_ch1"
    completed: bool
    quiz_score: float     # 0.0 - 1.0
    quiz_attempts: int
    last_accessed: str    # ISO 8601
    time_spent_seconds: int

class LabProgress:
    lab_id: str           # e.g. "m1"
    completed: bool
    exercises_done: list
    last_accessed: str
```

### 5.2 测验 (Quiz)

```python
class QuizQuestion:
    id: str
    type: str             # "single_choice" | "multi_choice" | "true_false"
    question: str
    options: list
    answer: object
    explanation: str

class QuizResult:
    chapter_id: str
    total_questions: int
    correct_count: int
    score: float          # 0.0 - 1.0
    answers: dict
    timestamp: str
```

### 5.3 交易心理 (Psychology)

```python
class PsychologyCheckRecord:
    timestamp: str
    scores: dict          # {question_key: 1-5}
    overall_risk_level: str  # "green" | "yellow" | "red"
    proceeded_to_trade: bool
    self_notes: str

class TradingJournalEntry:
    date: str
    setup_type: str       # H2 / L2 / FB / 其他
    entry_reason: str
    exit_reason: str
    pnl_pct: float
    emotional_state: str
    lesson_learned: str
    mistake_flag: bool
```

### 5.4 用户偏好 (UserPreferences)

```python
class UserPreferences:
    current_phase: str         # 当前学习阶段
    preferred_timeframe: str   # day | 60min | 15min
    sandbox_balance: float     # 沙盒虚拟资金（默认10万）
    achievements: list         # 已解锁成就
    risk_profile: str          # conservative | moderate | aggressive
```

### 5.5 SQLite 数据库

| 表名 | 用途 | 主键 |
|------|------|------|
| `chapter_progress` | 章节学习进度 | `chapter_id` |
| `lab_progress` | 实验室进度 | `lab_id` |
| `quiz_results` | 测验成绩历史 | `id` (AUTO) |
| `user_preferences` | 用户偏好（单行） | `id = 1` |
| `psychology_checks` | 心理自检记录 | `id` (AUTO) |
| `trading_journal` | 交易日志 | `id` (AUTO) |

---

## 6. 技术栈

| 层 | 技术 | 版本 | 用途 |
|----|------|------|------|
| 主前端 | Vue2 + Vue Router + Vuex | — | SPA 页面、路由、状态管理 |
| 主后端 | FastAPI | ≥0.100 | REST API、CORS、SPAS 代理 |
| 主题 | 自定义深色主题 | — | 黑底 + 金色强调 |
| 样式 | 自定义 CSS | — | 仪表盘卡片、时间线 |
| 图表 | ECharts | ≥5.17 | K线图、指标图 |
| 数据处理 | Pandas | ≥2.0 | 数据分析 |
| 配置解析 | PyYAML | ≥6.0 | 内容文件解析 |
| 数据库 | SQLite3 | 内置 | 进度持久化 |
| 测试 | Pytest | ≥7.4 | 单元/集成测试 |
| 跨服务通信 | httpx | ≥0.25 | Academy → SPAS API 代理 |
| SPAS SDK | SPAS Core API | ≥0.1.0 | 涨跌概率/Setup/风控/市场数据 |

---

## 7. Bridge 层接口

Bridge 位于 `core/bridge/`，用于读取 SPAS 本地数据（Parquet）和配置（sectors.yaml），供 Academy 后端使用。生产环境下，**涨跌概率/Setup 识别由 SPAS Core API 统一提供**，不通过 Bridge 计算。

### data_reader

```python
from core.bridge import (
    list_available_etfs,       # → list[dict]    列出所有可用 ETF
    load_etf_data,             # → DataFrame     加载 ETF OHLCV 数据
    load_all_etf_metadata,     # → DataFrame     所有 ETF 元数据概览
    get_etf_close_series,      # → Series        收盘价序列
    get_etf_display_name,      # → str           ETF 友好显示名
)
```

### SPAS Core API（学院后端通过 `/api/spas` 代理）

```python
# Vue2 前端直接调用 /api/spas/signal/{code}
GET /api/spas/signal/{code}          → SPAS 自动信号
GET /api/spas/market/etfs            → ETF 列表
GET /api/spas/market/etf/{code}/ohlcv → OHLCV 数据
GET /api/spas/system/status          → SPAS 系统状态
```

---

## 8. 关键设计决策

### 8.1 为什么采用 Vue2 + FastAPI 前后端分离架构？

- **Vue2 + FastAPI** 是主架构：前后端分离、更好的交互体验、可扩展为生产 Web 应用
- 前端通过 `/api/spas/*` 直接访问 SPAS 核心 API，通过 `/api/*` 访问 Academy 后端
- 前后端共享 `core/` 数据层和 `content/` 学习内容

### 8.2 为什么 SPAS 预测要由 SPAS Core API 统一提供？

- 保证全院/全系统只有一个预测引擎，避免多个模块各自实现导致口径冲突
- 预测算法、风控、回测等专业逻辑集中在 `src/`（SPAS 核心）
- 学院后端 `/api/spas` 仅做代理，便于统一 CORS 和入口管理

### 8.3 为什么有 Bridge 层？

- 集中管理跨系统数据读取，SPAS 数据格式变化时只需修改 Bridge
- 对外提供稳定的、语义化的接口
- 可 Mock 进行独立测试
- SPAS 数据不可用时自动回退

### 8.4 为什么内容用 Markdown 而不是数据库？

- Markdown 可版本管理（git diff 友好）
- 非技术人员也能编辑内容
- 内容与代码完全解耦
- 可被任何 Markdown 渲染器消费

---

## 9. 开发进度

### Phase 1: 骨架搭建 ✅ 已完成

- [x] 目录结构 + 独立依赖配置
- [x] 7 个数据模型（dataclass）
- [x] SQLite 6 表 + CRUD
- [x] Bridge: data_reader + knowledge_extractor
- [x] Content loader + Quiz widget
- [x] P1 第一章完整内容（Markdown + 测验 YAML）
- [x] M1 数据勘探实验室
- [x] 23 个自动化测试全部通过

### Phase 2: 前后端分离架构 ✅ 已完成

- [x] FastAPI 后端（多路由模块）
- [x] Vue2 SPA（页面 + 组件 + axios 封装）
- [x] SPAS 自动信号页面
- [x] 手动指标分析页面
- [x] K 线图组件（ECharts）
- [x] 交易沙盒、心理自检、交易日志、进度仪表盘

### Phase 3: 与 SPAS 核心统一 ✅ 已完成

- [x] SPAS Core API 端口统一为 8000
- [x] Academy 后端端口统一为 8001
- [x] Academy `/api/spas/*` 代理到 SPAS Core API
- [x] 手动指标分析独立为 `/api/manual-analysis/*`
- [x] Vue devServer 代理：/api/spas → 8000，/api → 8001
- [x] 一键启动脚本 `scripts/start_all.py`

### Phase 4: 内容填充 🔜

- [x] P1 全部 5 章
- [x] P2-P7 全部 29 章
- [ ] 部分章节测验题扩充
- [ ] M2-M6 实验室

### Phase 5: 完善 🔜

- [x] 学习进度仪表盘
- [ ] 术语表（可搜索）
- [ ] 回测分析器页面
- [ ] 特征实验室（参数调节 + 实时反馈）
- [ ] 市场情绪可视化

---

## 10. 常用命令

```bash
# 一键启动全栈（SPAS API + Academy 后端 + Vue 前端）
cd D:\stock_market
python scripts/start_all.py

# 仅启动 Academy 后端（手动）
cd D:\stock_market\investment_academy
uvicorn backend.main:app --host 127.0.0.1 --port 8001

# 启动 Vue2 前端（手动）
cd D:\stock_market\investment_academy\frontend
npm run serve

# 一键关闭
python scripts/stop_all.py

# 安装依赖
pip install -r requirements.txt

# 运行全部测试
python -m pytest tests/ -v
python -m pytest tests/ -v -m "not integration"

# 查看测试覆盖率
python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## 11. SPAS 知识资产来源

投资学院的知识内容源自 SPAS 项目中以下核心模块：

| SPAS 模块 | 提供的知识 |
|-----------|-----------|
| `bar_feature.py` | 6 维 K 线微观结构特征公式 |
| `market_state.py` | 三状态马尔可夫机（BULL/BEAR/NEUTRAL）+ ADX 趋势分类 |
| `setup_recog.py` | Wyckoff H2/L2/FB 模式识别 + 质量评分 |
| `fusion.py` | 多时间框架（MTF）4 框架投票融合 |
| `rule_engine.py` | 8 维规则向量 + 基率收缩估计 |
| `ml_model.py` | LightGBM/GBClassifier + Isotonic 概率校准 |
| `constraints.py` | 6 层硬约束风控 + Kelly 仓位公式 |
| `volatility.py` | 波动率锚定 + 仓位缩放 |
| `tail_risk.py` | 尾部风险检测 + 熔断 |
| `liquidity.py` | 3 层流动性检查 |
| `engine.py` | Walk-Forward 滚动回测引擎 |
| `forward_bias.py` | 前视偏差检测 + 严重程度分级 |
| `cost_model.py` | 佣金 + 印花税 + 滑点成本模型 |
| `graph.py` | 60+ 条产业链边的行业关联图 |
| `sentiment/collector.py` | 4 层优先级市场情绪采集 |
| `config/sectors.yaml` | 14 个行业 + ETF + 成分股定义 |
| `config/settings.yaml` | 全系统参数配置（13 ETF × 726 天实证） |

---

## 12. Git 提交历史

```
450bca0 fix(academy): fix _get_conn default arg bug + add integration marker + conftest
3f588c3 feat(academy): add P1 basics knowledge page
ed49dc7 feat(academy): add Streamlit main entry with dual-track navigation
a31e72d feat(academy): add content loader, quiz widget, and P1 chapter 1
f8e9b3b feat(academy): add Bridge knowledge_extractor
0c75b29 feat(academy): add Bridge data_reader -- parquet ETF data access
0b16984 feat(academy): add SQLite persistence layer with repository functions
a731fef feat(academy): add data models — progress, quiz, user, psychology
2da9d69 fix(academy): add root __init__.py and clarify requirements.txt
c55767b feat(investment-academy): Task 1 — create directory structure and project config
```

---

> **设计规格**: `docs/superpowers/specs/2026-06-30-investment-academy-design.md`
> **实施计划**: `docs/superpowers/plans/2026-07-01-investment-academy-plan.md`
> **构建日期**: 2026-07-01
