# Investment Academy — FastAPI + Vue2 前后端分离设计规格

> **日期**: 2026-07-01
> **状态**: approved
> **上游**: [investment-academy-design.md](./2026-06-30-investment-academy-design.md)

---

## 1. 目标

将 investment_academy 从 Streamlit 单体应用重构为 **前后端分离架构**（Streamlit 已移除）：

- **前端**: Vue2 SPA（`localhost:8080`）
- **后端**: FastAPI（`localhost:8001`），代理 `/api/spas/*` 到 SPAS Core API（`localhost:8000`）
- **数据**: 全部本地 — Parquet（SPAS）、SQLite（进度）、Markdown/YAML（内容）
- **用户模型**: 单用户，无认证

## 2. 架构全景

```
┌─────────────────────┐         HTTP/JSON          ┌──────────────────────┐
│   Vue2 SPA           │ ◄──────────────────────► │   FastAPI :8001       │
│   frontend/          │    axios + dev proxy      │   backend/            │
│                      │                           │                       │
│   Router → Views     │                           │   routers/ ─────────┐ │
│   Components         │                           │   schemas.py         │ │
│   Store              │                           │                      │ │
└─────────────────────┘                           │   ┌──────────────────┘ │
                                                    │   │ import            │
                                                    │   ▼                   │
                                                    │   ✅ models/          │
                                                    │   ✅ db/repository.py │
                                                    │   ✅ bridge/          │
                                                    │   ✅ engine/          │
                                                    │   ✅ content/         │
                                                    └──────────────────────┘
                              │
                              ▼ proxy /api/spas/*
                    ┌──────────────────────┐
                    │   SPAS Core API :8000 │
                    │   scripts/start.py serve
                    └──────────────────────┘
```

**核心原则**: 所有现有 Python 模块零改动。FastAPI 层是纯粹的新增代码，通过 `import` 消费现有模块。

## 3. 目录结构

```
investment_academy/
│
├── backend/                          # FastAPI 应用
│   ├── __init__.py
│   ├── main.py                       # FastAPI app, CORS, health check
│   ├── schemas.py                    # Pydantic 请求/响应模型
│   └── routers/
│       ├── __init__.py
│       ├── content.py                # GET  学习内容（章节、测验题、实验指南）
│       ├── quiz.py                   # POST 测验提交 → 评分 + 持久化
│       ├── progress.py               # GET/POST  学习进度
│       ├── market.py                 # GET  ETF 数据（Bridge → Parquet）
│       ├── sandbox.py                # POST/GET  交易沙盒（内存会话）
│       ├── user.py                   # GET/PUT/POST  偏好 + 心理 + 日志
│       ├── spas.py                   # 代理 /api/spas/* → SPAS Core API :8000
│       └── manual_analysis.py        # 手动指标合成（独立功能）
│
├── frontend/                         # Vue2 SPA
│   ├── package.json
│   ├── vue.config.js                 # devServer.proxy → /api/spas :8000, /api :8001
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/                      # axios 封装（每个模块一个文件）
│       │   ├── index.js              # axios 实例 + 基础配置
│       │   ├── content.js
│       │   ├── quiz.js
│       │   ├── progress.js
│       │   ├── market.js
│       │   ├── sandbox.js
│       │   ├── user.js
│       │   ├── spas.js               # SPAS Core 代理接口
│       │   └── manual_analysis.js
│       ├── router/
│       │   └── index.js              # Vue Router 路由表
│       ├── store/                    # Vuex（进度、偏好等全局状态）
│       │   └── index.js
│       ├── styles/                   # 全局设计系统
│       │   ├── theme.css
│       │   └── components.css
│       ├── views/                    # 页面级组件
│       │   ├── Home.vue              # 首页（双轨导航）
│       │   ├── SPASSignal.vue
│       │   ├── SPASPrediction.vue
│       │   ├── MarketOverview.vue
│       │   ├── ProgressDashboard.vue
│       │   ├── TradingJournal.vue
│       │   ├── PsychologyCheck.vue
│       │   ├── knowledge/
│       │   │   └── KnowledgePhase.vue    # 通用知识阶段页
│       │   └── practice/
│       │       ├── PracticeLab.vue       # 通用实践实验室页
│       │       └── Sandbox.vue
│       └── components/               # 可复用组件
│           ├── ui/                   # 设计系统组件
│           │   ├── Icon.vue
│           │   ├── Panel.vue
│           │   ├── MetricCard.vue
│           │   ├── Badge.vue
│           │   ├── Button.vue
│           │   ├── PageHeader.vue
│           │   ├── SectionTitle.vue
│           │   ├── ProbabilityRing.vue
│           │   └── FactorBar.vue
│           ├── QuizWidget.vue        # 测验组件
│           ├── KLineChart.vue        # K线图（ECharts）
│           ├── SandboxPanel.vue      # 交易沙盒面板
│           ├── ProgressBar.vue       # 进度条
│           └── MarkdownViewer.vue    # Markdown 渲染
│
├── core/                             # 共享核心库（Backend 与前端共用）
│   ├── models/                       # 数据模型（dataclass）
│   ├── db/                           # SQLite 持久化
│   ├── bridge/                       # SPAS 数据读取适配器
│   └── engine/                       # 内容加载 + 沙盒引擎
│
├── content/                          # 学习内容（Markdown + YAML）
├── tests/                            # 测试套件（60 个测试）
├── pyproject.toml                    # 独立依赖管理
└── requirements.txt                  # pip install 用
```

## 4. API 端点设计

### 4.1 内容系统 `routers/content.py`

| 方法 | 路径 | 返回 | 说明 |
|------|------|------|------|
| GET | `/api/content/phases` | `[{id, chapter_count, has_quiz}]` | 知识轨道阶段列表 |
| GET | `/api/content/labs` | `[{id, has_guide, has_exercises}]` | 实践实验室列表 |
| GET | `/api/content/chapter/{phase_id}/{filename}` | `{content: "markdown..."}` | 章节 Markdown 内容 |
| GET | `/api/content/quiz/{phase_id}` | `{chapter, questions: [...]}` | 测验配置 |
| GET | `/api/content/lab/{lab_id}` | `{guide: "markdown...", exercises: ...}` | 实验室内容 |

**实现**: 直接调用 `interactive.content_loader` 函数，无需任何改动。

### 4.2 测验系统 `routers/quiz.py`

| 方法 | 路径 | Body | 返回 | 说明 |
|------|------|------|------|------|
| POST | `/api/quiz/submit` | `{phase_id, chapter_id, answers: {q_id: answer}}` | `{score, correct_count, total, passed, explanations: [...]}` | 提交测验 → 评分 + 持久化 |

**实现**: 从 `interactive.quiz_widget.render_quiz` 提取评分逻辑（纯函数），结果写入 `db.repository.save_quiz_result` + `save_chapter_progress`。

### 4.3 学习进度 `routers/progress.py`

| 方法 | 路径 | 返回/Body | 说明 |
|------|------|------|------|
| GET | `/api/progress` | `[{chapter_id, completed, quiz_score, ...}]` | 全部章节进度 |
| GET | `/api/progress/{chapter_id}` | `{chapter_id, completed, quiz_score, ...}` | 单个章节进度 |
| POST | `/api/progress/{chapter_id}` | body: `{completed, quiz_score, time_spent_seconds}` | 更新进度 |

**实现**: 直接调用 `db.repository` 的 `get_all_chapter_progress`、`get_chapter_progress`、`save_chapter_progress`。

### 4.4 市场数据 `routers/market.py`

| 方法 | 路径 | 返回 | 说明 |
|------|------|------|------|
| GET | `/api/market/etfs` | `[{code, market, file, has_5min}]` | 可用 ETF 列表 |
| GET | `/api/market/etfs/meta` | `[{code, rows, start_date, end_date}]` | ETF 元数据总览 |
| GET | `/api/market/etf/{code}/name` | `{code, display_name}` | ETF 友好名称 |
| GET | `/api/market/etf/{code}/ohlcv?tf=day&limit=180` | `{bars: [{date, open, high, low, close, volume}]}` | OHLCV 数据（K线图用） |

**实现**: 直接调用 `bridge.data_reader` 函数，DataFrame 转 JSON。ETF 名称从 `get_etf_display_name` 获取。

### 4.5 交易沙盒 `routers/sandbox.py`

沙盒会话存储在内存 `dict` 中，key 为 `session_id`（UUID），value 为 `SandboxEngine` 实例。

| 方法 | 路径 | Body | 返回 | 说明 |
|------|------|------|------|------|
| POST | `/api/sandbox/init` | `{etf_code, timeframe?, initial_cash?}` | `{session_id}` | 初始化沙盒会话 |
| GET | `/api/sandbox/{sid}/state` | — | `{cash, shares, cost_basis, is_done, index, total_bars}` | 当前状态 |
| GET | `/api/sandbox/{sid}/bar` | — | `{date, open, high, low, close, volume, index, is_last}` | 当前 K 线 |
| POST | `/api/sandbox/{sid}/advance` | — | `{bar, is_done}` | 前进到下一根 bar |
| GET | `/api/sandbox/{sid}/can-buy` | — | `{can, message}` | 检查能否买入 |
| POST | `/api/sandbox/{sid}/buy` | `{shares, reason?}` | `{trade, bar}` | 执行买入 |
| GET | `/api/sandbox/{sid}/can-sell` | — | `{can, message}` | 检查能否卖出 |
| POST | `/api/sandbox/{sid}/sell` | `{shares?, reason?}` | `{trade, bar}` | 执行卖出 |
| GET | `/api/sandbox/{sid}/portfolio` | — | `{cash, shares, price, value, unrealized_pnl, unrealized_pnl_pct}` | 组合状态 |
| GET | `/api/sandbox/{sid}/performance` | — | `PerformanceReport` 对象 | 完整绩效报告 |
| GET | `/api/sandbox/{sid}/equity-curve` | — | `[{date, value, cash, shares, price}]` | 权益曲线数据 |

**实现**: 直接使用 `interactive.sandbox_engine.SandboxEngine`。状态默认 30 分钟超时自动清理。

### 4.6 用户系统 `routers/user.py`

| 方法 | 路径 | Body | 返回 | 说明 |
|------|------|------|------|------|
| GET | `/api/user/preferences` | — | `UserPreferences` | 获取偏好 |
| PUT | `/api/user/preferences` | `UserPreferences` | `UserPreferences` | 更新偏好 |
| POST | `/api/user/psychology-check` | `PsychologyCheckRecord` | `{id}` | 记录心理自检 |
| GET | `/api/user/psychology-history` | — | `[PsychologyCheckRecord]` | 历史记录 |
| POST | `/api/user/journal` | `TradingJournalEntry` | `{id}` | 记录交易日志 |
| GET | `/api/user/journal` | — | `[TradingJournalEntry]` | 日志列表 |

**实现**: 直接调用 `db.repository` 对应函数。

### 4.8 SPAS 代理 `routers/spas.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/spas/signal/{code}` | 对指定 ETF 运行完整 SPAS 流水线（代理到 SPAS Core :8000） |
| GET | `/api/spas/market/etfs` | 可用 ETF 列表 |
| GET | `/api/spas/market/etf/{code}/ohlcv` | ETF OHLCV 数据 |
| GET | `/api/spas/system/status` | SPAS 系统状态 |

### 4.9 手动指标分析 `routers/manual_analysis.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/manual-analysis/analysis/{code}` | 手动指标合成 |
| GET | `/api/manual-analysis/system-info` | 数据状态 |
| GET | `/api/manual-analysis/history` | 历史记录 |

### 4.10 系统 `main.py`

| 方法 | 路径 | 返回 | 说明 |
|------|------|------|------|
| GET | `/api/health` | `{status: "ok", timestamp}` | 健康检查 |

## 5. Pydantic Schema 设计

```python
# backend/schemas.py 核心模型

class ChapterProgressOut(BaseModel):
    chapter_id: str
    completed: bool
    quiz_score: float
    quiz_attempts: int
    last_accessed: Optional[str]
    time_spent_seconds: int

class QuizSubmitIn(BaseModel):
    phase_id: str
    chapter_id: str
    answers: dict[str, Any]          # {question_id: user_answer}

class QuizSubmitOut(BaseModel):
    score: float
    correct_count: int
    total: int
    passed: bool                      # score >= 0.6
    explanations: list[dict]          # [{question_id, correct_answer, explanation}]

class OHLCVBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class SandboxInitIn(BaseModel):
    etf_code: str
    timeframe: str = "day"
    initial_cash: float = 100000.0

class SandboxStateOut(BaseModel):
    session_id: str
    cash: float
    shares: int
    cost_basis: float
    index: int
    total_bars: int
    is_done: bool

class TradeOut(BaseModel):
    date: str
    action: str
    price: float
    shares: int
    amount: float
    reason: str
    cost: float

class UserPreferencesIn(BaseModel):
    current_phase: str = "p1"
    preferred_timeframe: str = "day"
    sandbox_balance: float = 100000.0
    achievements: list[str] = []
    risk_profile: str = "moderate"
```

## 6. 关键技术决策

### 6.1 同步路由（def，非 async def）

所有路由使用 `def`（同步），因为现有 `db/repository.py` 使用 `sqlite3`（同步），`bridge/data_reader.py` 使用 `pandas`（同步）。同步路由在 FastAPI 中在线程池中运行，对单用户场景没有任何性能损失。

### 6.2 数据路径处理

```python
# backend/ 的 sys.path 设置（main.py 前几行）
BACKEND_DIR = Path(__file__).resolve().parent
ACADEMY_ROOT = BACKEND_DIR.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

# 然后正常 import
from db.repository import get_all_chapter_progress
from bridge.data_reader import list_available_etfs
```

数据库路径由 `db/repository.py` 内部的 `DB_PATH` 决定，基于其自身文件位置计算，无需额外配置。

### 6.3 沙盒会话管理

- 内存 `dict[str, SandboxEngine]`，key 为 UUID
- 无过期清理（单用户即用即弃），可后续加 30 分钟 TTL
- `init` 返回 `session_id`，后续请求携带此 ID

### 6.4 测验评分逻辑提取

从 `core/engine/quiz_engine.py`（或原 `interactive/quiz_widget.py`）的渲染逻辑中提取纯评分函数：

```python
# backend/routers/quiz.py 中新建
def score_quiz(questions: list[QuizQuestion], answers: dict) -> tuple[int, int, list[dict]]:
    """纯函数：评分并返回解析"""
    correct = 0
    explanations = []
    for q in questions:
        user_ans = answers.get(q.id)
        is_correct = (user_ans == q.answer) or (
            isinstance(q.answer, list) and isinstance(user_ans, list)
            and set(user_ans) == set(q.answer)
        )
        if is_correct:
            correct += 1
        explanations.append({
            "question_id": q.id,
            "correct_answer": q.answer,
            "explanation": q.explanation,
            "user_correct": is_correct,
        })
    return correct, len(questions), explanations
```

### 6.5 前端开发代理

```javascript
// frontend/vue.config.js
module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/api/spas': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  }
}
```

Vue2 开发时 `/api/spas/*` 自动代理到 SPAS Core API（:8000），其余 `/api/*` 代理到 Academy Backend（:8001），无需在浏览器端处理 CORS。FastAPI 端仍配置 CORS 作为后备。

### 6.6 依赖关系

- 前端只通过 HTTP 调用后端/SPAS API，不直接引用 `core/`
- 后端 `backend/routers/*` 引用 `core/` 的模型、数据库、Bridge 和内容加载器
- `core/` 作为共享库，可被后端独立测试，也可被未来其他前端复用

## 7. 依赖变更

```diff
# pyproject.toml 新增/保留
dependencies = [
    "pandas>=2.0",
    "pyyaml>=6.0",
+   "fastapi>=0.100",
+   "uvicorn[standard]>=0.30",
+   "httpx>=0.25",
]
```

前端依赖（`frontend/package.json`）：
- `vue@2`
- `vue-router@3`
- `vuex@3`
- `axios`
- `marked`（Markdown 渲染）
- `echarts`（K 线图）
- `klinecharts`（K 线图组件库）

## 8. 启动方式

推荐一键启动：

```bash
cd D:\stock_market
python scripts/start_all.py
```

该脚本同时启动：
- SPAS Core API — http://127.0.0.1:8000
- Investment Academy Backend — http://127.0.0.1:8001
- Vue2 Frontend — http://127.0.0.1:8080

手动启动（三个终端）：

```bash
# 终端 1: 启动 SPAS Core API
cd D:\stock_market
python scripts/start.py serve

# 终端 2: 启动 Academy 后端
cd D:\stock_market\investment_academy
uvicorn backend.main:app --host 127.0.0.1 --port 8001

# 终端 3: 启动前端
cd D:\stock_market\investment_academy\frontend
npm install
npm run serve
```

浏览器打开 http://localhost:8080。

- SPAS Core Swagger: http://127.0.0.1:8000/docs
- Academy Backend Swagger: http://127.0.0.1:8001/docs

一键关闭：

```bash
cd D:\stock_market
python scripts/stop_all.py
```

## 9. 测试策略

### 后端测试（`tests/test_backend/`、`tests/test_models/`、`tests/test_db/`、`tests/test_bridge/`、`tests/test_engine/`、`tests/test_content/`）

- `test_content_routes.py` — 验证内容 API 返回正确数据
- `test_quiz_routes.py` — 验证评分逻辑和持久化
- `test_progress_routes.py` — 验证进度 CRUD
- `test_market_routes.py` — 验证 Bridge 数据接口
- `test_sandbox_routes.py` — 验证沙盒会话生命周期
- `test_user_routes.py` — 验证偏好/心理/日志接口
- `test_spas_routes.py` — 验证 SPAS 代理路由
- 现有模型/数据库/Bridge/内容测试继续保留

使用 FastAPI `TestClient`，不启动真实服务器。当前测试总数：60 个。

### 前端测试（可选项）

- Vue 组件单元测试（Jest + vue-test-utils）
- 不在本次范围

### 全量验证

```bash
# 根目录
cd D:\stock_market
python -m pytest tests/ -q

# Academy 子目录
cd D:\stock_market\investment_academy
python -m pytest tests/ -q

# 前端构建
cd D:\stock_market\investment_academy\frontend
npm run build
```

## 10. 阶段规划

### Phase 1: 后端骨架 ✅
- `backend/main.py` + CORS + health check
- `backend/schemas.py`
- 路由：`content.py`、`quiz.py`、`progress.py`、`user.py`、`market.py`、`sandbox.py`
- 路由：`spas.py`（SPAS Core 代理）、`manual_analysis.py`
- 后端单元测试

### Phase 2: 前端骨架 ✅
- Vue2 项目初始化
- `vue.config.js` 代理配置（/api/spas → 8000，/api → 8001）
- 路由 + 状态管理
- `api/` axios 封装
- 基础布局 + 导航
- 全局设计系统（theme.css, components.css, ui/ components）

### Phase 3: 核心页面 ✅
- 首页（双轨导航）
- 知识阶段通用页 `KnowledgePhase.vue`（章节阅读 + 测验）
- 实践实验室通用页 `PracticeLab.vue`（ETF 浏览器 + K线图）
- SPAS 自动信号页 `SPASSignal.vue`
- SPAS 预测页 `SPASPrediction.vue`
- 市场概览 `MarketOverview.vue`

### Phase 4: 完善 ✅
- 交易沙盒 `Sandbox.vue`
- 交易日志 `TradingJournal.vue`
- 心理自检 `PsychologyCheck.vue`
- 进度仪表盘 `ProgressDashboard.vue`
- 一键启动/关闭脚本 `scripts/start_all.py`、`scripts/stop_all.py`
- 移除 Streamlit 遗留代码
