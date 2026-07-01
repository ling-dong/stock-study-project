# Investment Academy — FastAPI + Vue2 前后端分离设计规格

> **日期**: 2026-07-01
> **状态**: approved
> **上游**: [investment-academy-design.md](./2026-06-30-investment-academy-design.md)

---

## 1. 目标

将 investment_academy 从 Streamlit 单体应用重构为 **前后端分离架构**：

- **前端**: Vue2 SPA（`localhost:8080`）
- **后端**: FastAPI（`localhost:8000`）
- **数据**: 全部本地 — Parquet（SPAS）、SQLite（进度）、Markdown/YAML（内容）
- **用户模型**: 单用户，无认证

## 2. 架构全景

```
┌─────────────────────┐         HTTP/JSON          ┌──────────────────────┐
│   Vue2 SPA           │ ◄──────────────────────► │   FastAPI :8000       │
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
                                                    │   ✅ interactive/     │
                                                    │   ✅ content/         │
                                                    └──────────────────────┘
```

**核心原则**: 所有现有 Python 模块零改动。FastAPI 层是纯粹的新增代码，通过 `import` 消费现有模块。

## 3. 目录结构

```
investment_academy/
│
├── backend/                          # 🆕 FastAPI 应用（约 400 行新增代码）
│   ├── __init__.py
│   ├── main.py                       # FastAPI app, CORS, static mount（备用）
│   ├── schemas.py                    # Pydantic 请求/响应模型（~80 行）
│   └── routers/
│       ├── __init__.py
│       ├── content.py                # GET  学习内容（章节、测验题、实验指南）
│       ├── quiz.py                   # POST 测验提交 → 评分 + 持久化
│       ├── progress.py               # GET/POST  学习进度
│       ├── market.py                 # GET  ETF 数据（Bridge → Parquet）
│       ├── sandbox.py                # POST/GET  交易沙盒（内存会话）
│       └── user.py                   # GET/PUT/POST  偏好 + 心理 + 日志
│
├── frontend/                         # 🆕 Vue2 SPA
│   ├── package.json
│   ├── vue.config.js                 # devServer.proxy → localhost:8000
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
│       │   └── user.js
│       ├── router/
│       │   └── index.js              # Vue Router 路由表
│       ├── store/                    # Vuex（进度、偏好等全局状态）
│       │   └── index.js
│       ├── views/                    # 页面级组件
│       │   ├── Home.vue              # 首页（双轨导航）
│       │   ├── knowledge/            # 知识轨道页面
│       │   │   └── P1Basics.vue
│       │   └── practice/             # 实践轨道页面
│       │       └── M1DataLab.vue
│       └── components/               # 可复用组件
│           ├── QuizWidget.vue        # 测验组件
│           ├── KLineChart.vue        # K线图（Plotly.js 或 ECharts）
│           ├── SandboxPanel.vue      # 交易沙盒面板
│           ├── ProgressBar.vue       # 进度条
│           └── MarkdownViewer.vue    # Markdown 渲染
│
├── models/                           # ✅ 不变（dataclass）
├── db/                               # ✅ 不变（schema.sql + repository.py）
├── bridge/                           # ✅ 不变（Parquet + YAML 读取）
├── interactive/                      # ✅ 不变（content_loader, sandbox_engine）
├── content/                          # ✅ 不变（Markdown + YAML）
├── pages/                            # ✅ 保留（Streamlit 继续可用）
├── tests/                            # ✅ 保留，新增 backend 单元测试
├── app.py                            # ✅ 保留（Streamlit 入口）
├── pyproject.toml                    # ✏️ 添加 fastapi, uvicorn
└── requirements.txt                  # ✏️ 添加 fastapi>=0.100, uvicorn>=0.30
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

### 4.7 系统 `main.py`

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

从 `interactive/quiz_widget.py` 的 Streamlit 渲染中提取纯评分函数：

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
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}
```

Vue2 开发时所有 `/api/*` 请求自动代理到 FastAPI，无需在浏览器端处理 CORS。FastAPI 端仍配置 CORS 作为后备。

### 6.6 现有 Streamlit 继续可用

以下文件零改动：
- `models/` — dataclass 定义
- `db/` — schema + repository
- `bridge/` — data_reader + knowledge_extractor
- `interactive/` — content_loader + sandbox_engine
- `content/` — Markdown + YAML
- `pages/` — Streamlit 页面
- `app.py` — Streamlit 入口

`streamlit run app.py` 仍然可以启动学习系统，与 FastAPI 后端共享同一套数据层。

## 7. 依赖变更

```diff
# pyproject.toml 新增
dependencies = [
    "streamlit>=1.28",
    "plotly>=5.17",
    "pandas>=2.0",
    "pyyaml>=6.0",
+   "fastapi>=0.100",
+   "uvicorn[standard]>=0.30",
]
```

前端依赖（`frontend/package.json`）：
- `vue@2`
- `vue-router@3`
- `vuex@3`
- `axios`
- `marked`（Markdown 渲染）
- `echarts`（K 线图，替代 Plotly）

## 8. 启动方式

```bash
# 终端 1: 启动后端
cd investment_academy
pip install fastapi uvicorn
uvicorn backend.main:app --reload --port 8000

# 终端 2: 启动前端
cd investment_academy/frontend
npm install
npm run serve

# 浏览器打开 http://localhost:8080
```

FastAPI 自动生成 Swagger 文档：`http://localhost:8000/docs`

## 9. 测试策略

### 后端测试（新增 `tests/test_backend/`）

- `test_content_routes.py` — 验证内容 API 返回正确数据
- `test_quiz_routes.py` — 验证评分逻辑和持久化
- `test_progress_routes.py` — 验证进度 CRUD
- `test_market_routes.py` — 验证 Bridge 数据接口
- `test_sandbox_routes.py` — 验证沙盒会话生命周期
- `test_user_routes.py` — 验证偏好/心理/日志接口

使用 FastAPI `TestClient`，不启动真实服务器。

### 现有测试（`tests/`）

全部保留，23 个测试继续通过（它们测试 models/db/bridge/interactive 层，与 FastAPI 无关）。

### 前端测试（可选项）

- Vue 组件单元测试（Jest + vue-test-utils）
- 不在本次范围

## 10. 阶段规划

### Phase 1: 后端骨架
- `backend/main.py` + CORS
- `backend/schemas.py`
- 路由：`content.py`、`quiz.py`、`progress.py`、`user.py`
- 路由：`market.py`、`sandbox.py`
- 后端单元测试

### Phase 2: 前端骨架
- Vue2 项目初始化（`vue create`）
- `vue.config.js` 代理配置
- 路由 + 状态管理
- `api/` axios 封装
- 基础布局 + 导航

### Phase 3: 核心页面
- 首页（双轨导航）
- P1 基础知识页（章节阅读 + 测验）
- M1 数据勘探实验室（ETF 浏览器 + K 线图）

### Phase 4: 完善
- 沙盒交易页面
- 进度仪表盘
- 其他阶段页面
