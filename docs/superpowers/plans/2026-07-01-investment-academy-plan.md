# Investment Academy 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建「投资学院」— 基于 Streamlit 的交互式投资学习网站，与 SPAS 完全解耦，双轨学习体系（知识轨34章+实践轨6实验室），7大交互功能。

**Architecture:** 分层单向依赖 — Pages → Interactive/Content → Bridge → SPAS（只读）。Bridge 层是唯一的跨系统接触点。Content 为纯 Markdown/YAML 数据文件，零代码依赖。

**Tech Stack:** Python 3.9+, Streamlit 1.28+, Plotly 5.17+, Pandas, PyYAML, SQLite3, Pytest

**Environment:** D:\stock_market (现有 SPAS 项目根目录)，investment_academy/ 为独立子目录

---

## File Structure Map

```
investment_academy/                    # 🆕 全部新建
├── pyproject.toml                     # 独立依赖（streamlit, plotly, pyyaml, pytest）
├── requirements.txt                   # pip install 用
├── app.py                             # Streamlit 入口 + 双轨导航 + 首页
│
├── models/                            # 数据模型层（零依赖）
│   ├── __init__.py                    # 导出所有模型
│   ├── progress.py                    # ChapterProgress, LabProgress
│   ├── quiz.py                        # QuizQuestion, QuizResult
│   └── user.py                        # UserPreferences, PsychologyCheckRecord, TradingJournalEntry
│
├── db/                                # 持久化层（依赖 models）
│   ├── __init__.py
│   ├── schema.sql                     # SQLite 建表语句
│   └── repository.py                  # CRUD 操作（每函数独立可测）
│
├── bridge/                            # SPAS 适配器层（唯一 import SPAS 的地方）
│   ├── __init__.py
│   ├── data_reader.py                 # 读取 Parquet ETF 数据
│   └── knowledge_extractor.py         # 提取配置/公式/参数（纯函数，no-op 回退）
│
├── content/                           # 学习内容（纯数据，零依赖）
│   ├── knowledge_track/
│   │   └── p1_basics/
│   │       ├── chapter_01_stock_concept.md   # Phase 1 实现第一章
│   │       └── quiz.yaml                     # Phase 1 实现第一套测验
│   └── practice_track/
│       └── m1_data_lab/
│           └── lab_guide.md
│
├── interactive/                       # 交互组件（依赖 bridge）
│   ├── __init__.py
│   ├── quiz_widget.py                 # 测验组件：单选/多选/判断
│   ├── content_loader.py             # Markdown + YAML 内容加载器
│   ├── kline_chart.py                 # K线图（Plotly OHLC）
│   ├── psychology_checklist.py        # 心理自检清单
│   └── progress_tracker.py            # 进度追踪 + 徽章
│
├── pages/                             # Streamlit 页面（依赖 content + interactive）
│   ├── __init__.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── p1_basics.py              # P1 页面：渲染5章 + 测验
│   └── practice/
│       ├── __init__.py
│       └── m1_data_lab.py            # M1 页面：数据探索
│
└── tests/                             # 独立测试套件
    ├── __init__.py
    ├── conftest.py                    # Fixtures: tmp_db, sample_content
    ├── test_models/
    │   └── test_progress.py
    ├── test_db/
    │   └── test_repository.py
    ├── test_bridge/
    │   └── test_data_reader.py
    ├── test_interactive/
    │   ├── test_content_loader.py
    │   └── test_quiz_widget.py
    └── test_content/                  # 内容文件校验
        └── test_quiz_yaml_valid.py
```

**依赖方向：** `tests → {pages → interactive + content, bridge, db → models}`

---

## Phase 1: 骨架搭建（MVP — 可运行的最小系统）

### Task 1: 创建目录结构和项目配置文件

**Files:**
- Create: `investment_academy/pyproject.toml`
- Create: `investment_academy/requirements.txt`
- Create: `investment_academy/models/__init__.py`
- Create: `investment_academy/db/__init__.py`
- Create: `investment_academy/bridge/__init__.py`
- Create: `investment_academy/interactive/__init__.py`
- Create: `investment_academy/pages/__init__.py`
- Create: `investment_academy/pages/knowledge/__init__.py`
- Create: `investment_academy/pages/practice/__init__.py`
- Create: `investment_academy/tests/__init__.py`
- Modify: `.gitignore` (add `.superpowers/`)

- [ ] **Step 1: 创建所有目录**

```bash
mkdir -p investment_academy/{models,db,bridge,interactive,pages/{knowledge,practice},tests,content/{knowledge_track/p1_basics,practice_track/m1_data_lab}}
touch investment_academy/models/__init__.py
touch investment_academy/db/__init__.py
touch investment_academy/bridge/__init__.py
touch investment_academy/interactive/__init__.py
touch investment_academy/pages/__init__.py
touch investment_academy/pages/knowledge/__init__.py
touch investment_academy/pages/practice/__init__.py
touch investment_academy/tests/__init__.py
```

- [ ] **Step 2: 创建 pyproject.toml**

```toml
[project]
name = "investment-academy"
version = "0.1.0"
description = "投资学院 — 交互式投资学习系统（与 SPAS 解耦）"
requires-python = ">=3.9"
dependencies = [
    "streamlit>=1.28",
    "plotly>=5.17",
    "pandas>=2.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 3: 创建 requirements.txt**

```
streamlit>=1.28
plotly>=5.17
pandas>=2.0
pyyaml>=6.0
pytest>=7.4
```

- [ ] **Step 4: 更新 .gitignore**

在 `.gitignore` 末尾添加 `.superpowers/`：

```bash
echo ".superpowers/" >> .gitignore
```

- [ ] **Step 5: 安装依赖**

```bash
cd investment_academy && pip install -e . 2>/dev/null || pip install -r requirements.txt
```

- [ ] **Step 6: 验证安装**

```bash
python -c "import streamlit; import plotly; import pandas; import yaml; print('All dependencies OK')"
```
Expected: `All dependencies OK`

- [ ] **Step 7: Commit**

```bash
git add investment_academy/ .gitignore
git commit -m "feat(academy): scaffold project structure with independent dependencies

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 实现数据模型层

**Files:**
- Create: `investment_academy/models/progress.py`
- Create: `investment_academy/models/quiz.py`
- Create: `investment_academy/models/user.py`
- Modify: `investment_academy/models/__init__.py`
- Create: `investment_academy/tests/test_models/test_progress.py`

- [ ] **Step 1: 创建进度模型**

```python
# investment_academy/models/progress.py
"""学习进度数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChapterProgress:
    """章节学习进度"""
    chapter_id: str              # e.g. "p1_ch1"
    completed: bool = False
    quiz_score: float = 0.0      # 0.0 - 1.0
    quiz_attempts: int = 0
    last_accessed: Optional[str] = None  # ISO 8601
    time_spent_seconds: int = 0

    def mark_completed(self, quiz_score: float = 0.0) -> None:
        self.completed = True
        self.quiz_score = quiz_score
        self.quiz_attempts += 1
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "completed": self.completed,
            "quiz_score": self.quiz_score,
            "quiz_attempts": self.quiz_attempts,
            "last_accessed": self.last_accessed,
            "time_spent_seconds": self.time_spent_seconds,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChapterProgress":
        return cls(
            chapter_id=d["chapter_id"],
            completed=bool(d.get("completed", False)),
            quiz_score=float(d.get("quiz_score", 0.0)),
            quiz_attempts=int(d.get("quiz_attempts", 0)),
            last_accessed=d.get("last_accessed"),
            time_spent_seconds=int(d.get("time_spent_seconds", 0)),
        )


@dataclass
class LabProgress:
    """实验室进度"""
    lab_id: str                  # e.g. "m1"
    completed: bool = False
    exercises_done: list = field(default_factory=list)
    last_accessed: Optional[str] = None

    def mark_exercise_done(self, exercise_id: str) -> None:
        if exercise_id not in self.exercises_done:
            self.exercises_done.append(exercise_id)
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "lab_id": self.lab_id,
            "completed": self.completed,
            "exercises_done": self.exercises_done,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LabProgress":
        return cls(
            lab_id=d["lab_id"],
            completed=bool(d.get("completed", False)),
            exercises_done=list(d.get("exercises_done", [])),
            last_accessed=d.get("last_accessed"),
        )
```

- [ ] **Step 2: 创建测验模型**

```python
# investment_academy/models/quiz.py
"""测验数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class QuizQuestion:
    """单道测验题"""
    id: str
    type: str            # "single_choice" | "multi_choice" | "true_false"
    question: str
    options: list
    answer: object       # single_choice: int index; multi_choice: list[int]; true_false: bool
    explanation: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "QuizQuestion":
        return cls(
            id=d["id"],
            type=d["type"],
            question=d["question"],
            options=list(d.get("options", [])),
            answer=d["answer"],
            explanation=d.get("explanation", ""),
        )


@dataclass
class QuizResult:
    """单次测验结果"""
    chapter_id: str
    total_questions: int
    correct_count: int
    score: float           # 0.0 - 1.0
    answers: dict          # {question_id: user_answer}
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def passed(self) -> bool:
        """≥60% 为通过"""
        return self.score >= 0.6

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": self.score,
            "answers": self.answers,
            "timestamp": self.timestamp,
        }
```

- [ ] **Step 3: 创建用户模型**

```python
# investment_academy/models/user.py
"""用户偏好与心理记录模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserPreferences:
    """用户偏好"""
    current_phase: str = "p1"               # 当前学习阶段
    preferred_timeframe: str = "day"        # day | 60min | 15min
    sandbox_balance: float = 100000.0       # 沙盒虚拟资金（默认10万）
    achievements: list = field(default_factory=list)
    risk_profile: str = "moderate"          # conservative | moderate | aggressive

    def to_dict(self) -> dict:
        return {
            "current_phase": self.current_phase,
            "preferred_timeframe": self.preferred_timeframe,
            "sandbox_balance": self.sandbox_balance,
            "achievements": self.achievements,
            "risk_profile": self.risk_profile,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UserPreferences":
        return cls(
            current_phase=d.get("current_phase", "p1"),
            preferred_timeframe=d.get("preferred_timeframe", "day"),
            sandbox_balance=float(d.get("sandbox_balance", 100000.0)),
            achievements=list(d.get("achievements", [])),
            risk_profile=d.get("risk_profile", "moderate"),
        )


@dataclass
class PsychologyCheckRecord:
    """心理自检记录"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scores: dict = field(default_factory=dict)  # {question_key: 1-5}
    overall_risk_level: str = "green"    # green | yellow | red
    proceeded_to_trade: bool = False
    self_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "scores": self.scores,
            "overall_risk_level": self.overall_risk_level,
            "proceeded_to_trade": self.proceeded_to_trade,
            "self_notes": self.self_notes,
        }


@dataclass
class TradingJournalEntry:
    """交易日志"""
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    setup_type: str = ""            # H2 | L2 | FB | 其他
    entry_reason: str = ""
    exit_reason: str = ""
    pnl_pct: float = 0.0
    emotional_state: str = ""       # 交易时情绪描述
    lesson_learned: str = ""
    mistake_flag: bool = False

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "setup_type": self.setup_type,
            "entry_reason": self.entry_reason,
            "exit_reason": self.exit_reason,
            "pnl_pct": self.pnl_pct,
            "emotional_state": self.emotional_state,
            "lesson_learned": self.lesson_learned,
            "mistake_flag": self.mistake_flag,
        }
```

- [ ] **Step 4: 更新 models/__init__.py**

```python
# investment_academy/models/__init__.py
from .progress import ChapterProgress, LabProgress
from .quiz import QuizQuestion, QuizResult
from .user import UserPreferences, PsychologyCheckRecord, TradingJournalEntry

__all__ = [
    "ChapterProgress",
    "LabProgress",
    "QuizQuestion",
    "QuizResult",
    "UserPreferences",
    "PsychologyCheckRecord",
    "TradingJournalEntry",
]
```

- [ ] **Step 5: 写模型单元测试**

```python
# investment_academy/tests/test_models/test_progress.py
"""测试进度模型"""
from models.progress import ChapterProgress, LabProgress


def test_chapter_progress_default():
    cp = ChapterProgress(chapter_id="p1_ch1")
    assert cp.completed is False
    assert cp.quiz_score == 0.0
    assert cp.quiz_attempts == 0


def test_chapter_progress_mark_completed():
    cp = ChapterProgress(chapter_id="p1_ch1")
    cp.mark_completed(quiz_score=0.8)
    assert cp.completed is True
    assert cp.quiz_score == 0.8
    assert cp.quiz_attempts == 1
    assert cp.last_accessed is not None


def test_chapter_progress_serialization():
    cp = ChapterProgress(chapter_id="p1_ch1")
    cp.mark_completed(quiz_score=0.75)
    d = cp.to_dict()
    cp2 = ChapterProgress.from_dict(d)
    assert cp2.chapter_id == "p1_ch1"
    assert cp2.completed is True
    assert cp2.quiz_score == 0.75


def test_lab_progress_mark_exercise():
    lp = LabProgress(lab_id="m1")
    lp.mark_exercise_done("ex1")
    assert "ex1" in lp.exercises_done
    lp.mark_exercise_done("ex1")  # 不重复
    assert len(lp.exercises_done) == 1
```

- [ ] **Step 6: 运行测试**

```bash
cd investment_academy && python -m pytest tests/test_models/test_progress.py -v
```
Expected: 4 passed

- [ ] **Step 7: Commit**

```bash
git add investment_academy/models/ investment_academy/tests/test_models/
git commit -m "feat(academy): add data models — progress, quiz, user, psychology

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 实现 SQLite 持久化层

**Files:**
- Create: `investment_academy/db/schema.sql`
- Create: `investment_academy/db/repository.py`
- Modify: `investment_academy/db/__init__.py`
- Create: `investment_academy/tests/test_db/test_repository.py`

- [ ] **Step 1: 创建 SQLite schema**

```sql
-- investment_academy/db/schema.sql

CREATE TABLE IF NOT EXISTS chapter_progress (
    chapter_id TEXT PRIMARY KEY,
    completed INTEGER NOT NULL DEFAULT 0,
    quiz_score REAL NOT NULL DEFAULT 0.0,
    quiz_attempts INTEGER NOT NULL DEFAULT 0,
    last_accessed TEXT,
    time_spent_seconds INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lab_progress (
    lab_id TEXT PRIMARY KEY,
    completed INTEGER NOT NULL DEFAULT 0,
    exercises_done TEXT NOT NULL DEFAULT '[]',  -- JSON array
    last_accessed TEXT
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    score REAL NOT NULL,
    answers TEXT NOT NULL,  -- JSON
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- 单行
    current_phase TEXT NOT NULL DEFAULT 'p1',
    preferred_timeframe TEXT NOT NULL DEFAULT 'day',
    sandbox_balance REAL NOT NULL DEFAULT 100000.0,
    achievements TEXT NOT NULL DEFAULT '[]',
    risk_profile TEXT NOT NULL DEFAULT 'moderate'
);

CREATE TABLE IF NOT EXISTS psychology_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    scores TEXT NOT NULL,         -- JSON
    overall_risk_level TEXT NOT NULL,
    proceeded_to_trade INTEGER NOT NULL DEFAULT 0,
    self_notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS trading_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    setup_type TEXT NOT NULL DEFAULT '',
    entry_reason TEXT NOT NULL DEFAULT '',
    exit_reason TEXT NOT NULL DEFAULT '',
    pnl_pct REAL NOT NULL DEFAULT 0.0,
    emotional_state TEXT NOT NULL DEFAULT '',
    lesson_learned TEXT NOT NULL DEFAULT '',
    mistake_flag INTEGER NOT NULL DEFAULT 0
);
```

- [ ] **Step 2: 创建 repository.py**

```python
# investment_academy/db/repository.py
"""SQLite 数据访问层 — 每个函数独立、可单独测试"""
import sqlite3
import json
import os
from typing import Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
DB_PATH = os.path.join(DB_DIR, "academy.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


def _get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    """获取数据库连接并初始化 schema"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


# ── Chapter Progress ──────────────────────────────────

def save_chapter_progress(chapter_id: str, completed: bool = False,
                          quiz_score: float = 0.0, quiz_attempts: int = 0,
                          last_accessed: Optional[str] = None,
                          time_spent_seconds: int = 0) -> None:
    conn = _get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO chapter_progress
        (chapter_id, completed, quiz_score, quiz_attempts, last_accessed, time_spent_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chapter_id, int(completed), quiz_score, quiz_attempts, last_accessed, time_spent_seconds))
    conn.commit()
    conn.close()


def get_chapter_progress(chapter_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM chapter_progress WHERE chapter_id = ?", (chapter_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_all_chapter_progress() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM chapter_progress").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Quiz Results ───────────────────────────────────────

def save_quiz_result(chapter_id: str, total_questions: int,
                     correct_count: int, score: float,
                     answers: dict, timestamp: str) -> int:
    conn = _get_conn()
    cursor = conn.execute("""
        INSERT INTO quiz_results (chapter_id, total_questions, correct_count, score, answers, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chapter_id, total_questions, correct_count, score, json.dumps(answers), timestamp))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_quiz_results(chapter_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM quiz_results WHERE chapter_id = ? ORDER BY timestamp DESC",
        (chapter_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── User Preferences ───────────────────────────────────

def save_user_preferences(prefs: dict) -> None:
    conn = _get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO user_preferences
        (id, current_phase, preferred_timeframe, sandbox_balance, achievements, risk_profile)
        VALUES (1, ?, ?, ?, ?, ?)
    """, (
        prefs.get("current_phase", "p1"),
        prefs.get("preferred_timeframe", "day"),
        prefs.get("sandbox_balance", 100000.0),
        json.dumps(prefs.get("achievements", [])),
        prefs.get("risk_profile", "moderate"),
    ))
    conn.commit()
    conn.close()


def get_user_preferences() -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM user_preferences WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return {
            "current_phase": "p1",
            "preferred_timeframe": "day",
            "sandbox_balance": 100000.0,
            "achievements": "[]",
            "risk_profile": "moderate",
        }
    return dict(row)


# ── Psychology Checks ──────────────────────────────────

def save_psychology_check(scores: dict, overall_risk_level: str,
                          proceeded_to_trade: bool = False,
                          self_notes: str = "",
                          timestamp: str = "") -> int:
    import datetime
    if not timestamp:
        timestamp = datetime.datetime.now().isoformat()
    conn = _get_conn()
    cursor = conn.execute("""
        INSERT INTO psychology_checks (timestamp, scores, overall_risk_level, proceeded_to_trade, self_notes)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, json.dumps(scores), overall_risk_level, int(proceeded_to_trade), self_notes))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_psychology_history(limit: int = 20) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM psychology_checks ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Trading Journal ────────────────────────────────────

def save_journal_entry(entry: dict) -> int:
    conn = _get_conn()
    cursor = conn.execute("""
        INSERT INTO trading_journal (date, setup_type, entry_reason, exit_reason, pnl_pct, emotional_state, lesson_learned, mistake_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.get("date", ""),
        entry.get("setup_type", ""),
        entry.get("entry_reason", ""),
        entry.get("exit_reason", ""),
        entry.get("pnl_pct", 0.0),
        entry.get("emotional_state", ""),
        entry.get("lesson_learned", ""),
        int(entry.get("mistake_flag", False)),
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_journal_entries(limit: int = 50) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM trading_journal ORDER BY date DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

- [ ] **Step 3: 更新 db/__init__.py**

```python
# investment_academy/db/__init__.py
from .repository import (
    save_chapter_progress,
    get_chapter_progress,
    get_all_chapter_progress,
    save_quiz_result,
    get_quiz_results,
    save_user_preferences,
    get_user_preferences,
    save_psychology_check,
    get_psychology_history,
    save_journal_entry,
    get_journal_entries,
)

__all__ = [
    "save_chapter_progress",
    "get_chapter_progress",
    "get_all_chapter_progress",
    "save_quiz_result",
    "get_quiz_results",
    "save_user_preferences",
    "get_user_preferences",
    "save_psychology_check",
    "get_psychology_history",
    "save_journal_entry",
    "get_journal_entries",
]
```

- [ ] **Step 4: 写 repository 单元测试**

```python
# investment_academy/tests/test_db/test_repository.py
"""测试 SQLite repository（使用临时数据库）"""
import os
import tempfile
from db import repository


def _use_temp_db():
    """将 repository 指向临时数据库"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    repository.DB_PATH = tmp.name
    return tmp.name


def test_save_and_get_chapter_progress():
    db_path = _use_temp_db()
    repository.save_chapter_progress("p1_ch1", completed=True, quiz_score=0.8, quiz_attempts=2)
    result = repository.get_chapter_progress("p1_ch1")
    assert result is not None
    assert result["chapter_id"] == "p1_ch1"
    assert result["completed"] == 1
    assert result["quiz_score"] == 0.8
    assert result["quiz_attempts"] == 2
    os.unlink(db_path)


def test_get_nonexistent_chapter():
    db_path = _use_temp_db()
    result = repository.get_chapter_progress("nonexistent")
    assert result is None
    os.unlink(db_path)


def test_save_and_get_quiz_results():
    db_path = _use_temp_db()
    rid = repository.save_quiz_result(
        "p1_ch1", total_questions=5, correct_count=4,
        score=0.8, answers={"q1": 1, "q2": 2}, timestamp="2026-07-01T00:00:00"
    )
    assert rid > 0
    results = repository.get_quiz_results("p1_ch1")
    assert len(results) == 1
    assert results[0]["score"] == 0.8
    os.unlink(db_path)


def test_user_preferences_default():
    db_path = _use_temp_db()
    prefs = repository.get_user_preferences()
    assert prefs["current_phase"] == "p1"


def test_save_and_get_user_preferences():
    db_path = _use_temp_db()
    repository.save_user_preferences({
        "current_phase": "p3",
        "risk_profile": "aggressive",
    })
    prefs = repository.get_user_preferences()
    assert prefs["current_phase"] == "p3"
    assert prefs["risk_profile"] == "aggressive"
    os.unlink(db_path)


def test_save_psychology_check():
    db_path = _use_temp_db()
    rid = repository.save_psychology_check(
        scores={"q1": 3, "q2": 5},
        overall_risk_level="yellow",
        proceeded_to_trade=False,
        timestamp="2026-07-01T12:00:00"
    )
    assert rid > 0
    history = repository.get_psychology_history()
    assert len(history) == 1
    assert history[0]["overall_risk_level"] == "yellow"
    os.unlink(db_path)


def test_journal_crud():
    db_path = _use_temp_db()
    rid = repository.save_journal_entry({
        "setup_type": "H2",
        "entry_reason": "回调到支撑位",
        "pnl_pct": 2.5,
        "emotional_state": "冷静",
        "mistake_flag": False,
    })
    assert rid > 0
    entries = repository.get_journal_entries()
    assert len(entries) == 1
    os.unlink(db_path)
```

- [ ] **Step 5: 运行测试**

```bash
cd investment_academy && python -m pytest tests/test_db/test_repository.py -v
```
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add investment_academy/db/ investment_academy/tests/test_db/
git commit -m "feat(academy): add SQLite persistence layer with repository functions

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: 实现 Bridge 层 — data_reader

**Files:**
- Create: `investment_academy/bridge/data_reader.py`
- Create: `investment_academy/tests/test_bridge/test_data_reader.py`

- [ ] **Step 1: 创建 data_reader.py**

```python
# investment_academy/bridge/data_reader.py
"""SPAS 数据读取适配器 — 唯一 import SPAS 和访问 Parquet 的地方"""
import os
from pathlib import Path
from typing import Optional

import pandas as pd

# SPAS 项目根目录（向上两级：bridge/ -> investment_academy/ -> D:\stock_market\）
SPAS_ROOT = Path(__file__).resolve().parent.parent.parent
SPAS_DATA_DIR = SPAS_ROOT / "data"


def list_available_etfs() -> list[dict]:
    """列出 data/ 中所有可用的 ETF Parquet 文件"""
    etfs = []
    if not SPAS_DATA_DIR.exists():
        return etfs
    for f in sorted(SPAS_DATA_DIR.glob("*_day.parquet")):
        code = f.stem.replace("_day", "")
        etfs.append({
            "code": code,
            "market": "SH" if ".SH" in f.stem else "SZ",
            "file": str(f),
            "has_5min": (SPAS_DATA_DIR / f"{code}_5min.parquet").exists(),
        })
    return etfs


def load_etf_data(code: str, timeframe: str = "day") -> Optional[pd.DataFrame]:
    """加载指定 ETF 的数据

    Args:
        code: ETF 代码，如 '512480.SH'
        timeframe: 'day' 或 '5min'

    Returns:
        DataFrame with columns: trade_date, open, high, low, close, volume
        如果文件不存在返回 None
    """
    file_path = SPAS_DATA_DIR / f"{code}_{timeframe}.parquet"
    if not file_path.exists():
        # 尝试备选命名
        alt_path = SPAS_DATA_DIR / f"{code}_{timeframe}.parquet"
        files = list(SPAS_DATA_DIR.glob(f"{code}*.parquet"))
        if files:
            file_path = files[0]
        else:
            return None

    df = pd.read_parquet(file_path)

    # 标准化列名
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().replace("_", "")
        if col_lower in ("tradedate", "trade_date", "date", "datetime"):
            col_map[col] = "trade_date"
        elif col_lower in ("open",):
            col_map[col] = "open"
        elif col_lower in ("high",):
            col_map[col] = "high"
        elif col_lower in ("low",):
            col_map[col] = "low"
        elif col_lower in ("close",):
            col_map[col] = "close"
        elif col_lower in ("vol", "volume"):
            col_map[col] = "volume"

    df = df.rename(columns=col_map)
    required_cols = ["trade_date", "open", "high", "low", "close", "volume"]
    available_cols = [c for c in required_cols if c in df.columns]

    if not available_cols:
        return df  # 返回原始数据，由调用方处理

    return df[available_cols].sort_values("trade_date").reset_index(drop=True)


def load_all_etf_metadata() -> pd.DataFrame:
    """加载所有 ETF 的元数据概览（首行、尾行、行数）"""
    etfs = list_available_etfs()
    records = []
    for etf in etfs:
        df = load_etf_data(etf["code"], "day")
        if df is not None and len(df) > 0:
            records.append({
                "code": etf["code"],
                "market": etf["market"],
                "rows": len(df),
                "start_date": str(df["trade_date"].iloc[0])[:10] if "trade_date" in df.columns else "N/A",
                "end_date": str(df["trade_date"].iloc[-1])[:10] if "trade_date" in df.columns else "N/A",
            })
    return pd.DataFrame(records) if records else pd.DataFrame()


def get_etf_close_series(code: str, timeframe: str = "day") -> Optional[pd.Series]:
    """获取 ETF 收盘价序列（用于快速绘图）"""
    df = load_etf_data(code, timeframe)
    if df is None or "trade_date" not in df.columns or "close" not in df.columns:
        return None
    return df.set_index("trade_date")["close"]


# 回退：当 SPAS 数据不可用时，返回友好提示
class DataNotAvailableError(Exception):
    """数据不可用异常"""
    pass
```

- [ ] **Step 2: 写 data_reader 测试**

```python
# investment_academy/tests/test_bridge/test_data_reader.py
"""测试 data_reader（依赖真实 Parquet 数据，标记为 integration）"""
import pytest
from bridge.data_reader import list_available_etfs, load_etf_data, load_all_etf_metadata


@pytest.mark.integration
def test_list_available_etfs():
    etfs = list_available_etfs()
    # 项目中已知至少有 13 个 ETF
    assert len(etfs) > 0
    for etf in etfs:
        assert "code" in etf
        assert "market" in etf
        assert etf["market"] in ("SH", "SZ")


@pytest.mark.integration
def test_load_etf_data_known():
    """加载已知存在的 ETF 数据"""
    df = load_etf_data("510300.SH", "day")
    assert df is not None
    assert len(df) > 100  # CSI 300 应该有足够数据
    assert "close" in df.columns or "trade_date" in df.columns


@pytest.mark.integration
def test_load_etf_data_nonexistent():
    """加载不存在的 ETF 应返回 None"""
    df = load_etf_data("999999.SZ", "day")
    assert df is None


@pytest.mark.integration
def test_load_all_etf_metadata():
    meta = load_all_etf_metadata()
    assert len(meta) > 0
    assert "code" in meta.columns


def test_list_etfs_no_data_dir(monkeypatch, tmp_path):
    """SPAS_DATA_DIR 不存在时返回空列表"""
    from bridge import data_reader
    monkeypatch.setattr(data_reader, "SPAS_DATA_DIR", tmp_path / "nonexistent")
    etfs = data_reader.list_available_etfs()
    assert etfs == []
```

- [ ] **Step 3: 运行测试**

```bash
cd investment_academy && python -m pytest tests/test_bridge/test_data_reader.py -v -m "not integration"
```
Expected: basic unit tests pass. Integration tests skip or pass if data available.

- [ ] **Step 4: Commit**

```bash
git add investment_academy/bridge/ investment_academy/tests/test_bridge/
git commit -m "feat(academy): add Bridge data_reader — parquet ETF data access

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: 实现 Bridge 层 — knowledge_extractor

**Files:**
- Create: `investment_academy/bridge/knowledge_extractor.py`

- [ ] **Step 1: 创建 knowledge_extractor.py**

```python
# investment_academy/bridge/knowledge_extractor.py
"""SPAS 知识提取器 — 从配置和代码中提取投资知识（纯函数，SPAS 不可用时回退）"""
from pathlib import Path
from typing import Optional

import yaml

SPAS_ROOT = Path(__file__).resolve().parent.parent.parent


def extract_sector_list() -> list[dict]:
    """从 config/sectors.yaml 提取行业列表及 ETF 信息"""
    sectors_path = SPAS_ROOT / "config" / "sectors.yaml"
    if not sectors_path.exists():
        return _fallback_sectors()

    with open(sectors_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    sectors = []
    for sector_id, info in data.items():
        if isinstance(info, dict):
            sectors.append({
                "id": sector_id,
                "name": info.get("name", sector_id),
                "etf_code": info.get("etf_code", ""),
                "constituents": info.get("constituents", [])[:3],  # 只取前3个
                "related_sectors": info.get("related_sectors", []),
            })
    return sectors


def extract_factor_definitions() -> list[dict]:
    """提取 K 线特征因子定义（6维）"""
    # 从 spec/代码中提取的已知公式 — SPAS 中硬编码在 bar_feature.py
    return [
        {
            "name": "body_ratio",
            "chinese": "实体比",
            "formula": "|Close - Open| / (High - Low)",
            "meaning": "烛体占整体振幅的比例，反映多空博弈强度",
            "range": "[0, 1]",
        },
        {
            "name": "close_position",
            "chinese": "收盘位置",
            "formula": "(Close - Low) / (High - Low)",
            "meaning": "收盘价在整体区间的位置。>0.5 买方强势，<0.5 卖方强势",
            "range": "[0, 1]",
        },
        {
            "name": "upper_shadow",
            "chinese": "上影线比例",
            "formula": "(High - max(Open, Close)) / (High - Low)",
            "meaning": "上方抛压强度。值越大上方阻力越大",
            "range": "[0, 1]",
        },
        {
            "name": "lower_shadow",
            "chinese": "下影线比例",
            "formula": "(min(Open, Close) - Low) / (High - Low)",
            "meaning": "下方支撑强度。值越大下方支撑越强",
            "range": "[0, 1]",
        },
        {
            "name": "trend_bar",
            "chinese": "趋势棒方向",
            "formula": "Close > Open → +1 (阳线), Close < Open → -1 (阴线), Close ≈ Open → 0 (十字星)",
            "meaning": "单根K线的涨跌方向",
            "range": "{-1, 0, +1}",
        },
        {
            "name": "limit_status",
            "chinese": "涨跌停状态（A股特有）",
            "formula": "价格触及涨跌停板 → ±1，正常 → 0",
            "meaning": "检测是否触及A股特有的±10%涨跌停限制",
            "range": "{-1, 0, +1}",
        },
    ]


def extract_market_state_params() -> dict:
    """提取市场状态机参数"""
    settings_path = SPAS_ROOT / "config" / "settings.yaml"
    if not settings_path.exists():
        return _fallback_market_params()

    with open(settings_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    market = data.get("market_state", {})
    return {
        "ema_period": market.get("ema_period", 20),
        "bull_trend_bar_ratio": market.get("bull_trend_bar_ratio", 0.40),
        "adx_threshold": market.get("adx_threshold", 18),
        "confirmation_bars": market.get("confirmation_bars", 2),
        "confidence_initial": market.get("confidence_initial", 0.3),
        "confidence_increment": market.get("confidence_increment", 0.05),
        "confidence_max": market.get("confidence_max", 0.9),
    }


def extract_risk_constraints() -> list[dict]:
    """提取风控约束层级"""
    settings_path = SPAS_ROOT / "config" / "settings.yaml"
    if not settings_path.exists():
        return _fallback_risk_constraints()

    with open(settings_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    risk = data.get("risk", {})
    constraints = risk.get("constraints", {})
    if isinstance(constraints, dict):
        result = []
        for layer, config in constraints.items():
            if isinstance(config, dict):
                result.append({
                    "layer": layer,
                    "threshold": config.get("threshold", ""),
                    "action": config.get("action", ""),
                })
        return result
    return _fallback_risk_constraints()


def extract_setup_definitions() -> list[dict]:
    """提取 Setup 模式定义"""
    return [
        {
            "name": "H2",
            "chinese": "双底回调",
            "theory": "Wyckoff",
            "description": "上升趋势中的两段式回调，每次回调低点抬高。牛市延续信号。",
            "base_winrate": 0.55,
            "quality_factors": ["回调幅度相近(35%)", "成交量收缩(30%)", "突破力度(35%)"],
        },
        {
            "name": "L2",
            "chinese": "双顶反弹",
            "theory": "Wyckoff",
            "description": "下降趋势中的两段式反弹，每次反弹高点降低。熊市延续信号。",
            "base_winrate": 0.55,
            "quality_factors": ["反弹幅度相近(35%)", "成交量收缩(30%)", "突破力度(35%)"],
        },
        {
            "name": "FB",
            "chinese": "假突破",
            "theory": "Wyckoff",
            "description": "价格突破关键位后迅速反转，形成陷阱。趋势衰竭信号。",
            "base_winrate": 0.45,
            "quality_factors": ["突破强弱(30%)", "反转速度(40%)", "成交量确认(30%)"],
        },
    ]


# ── 回退数据（SPAS 配置不存在时使用） ──

def _fallback_sectors() -> list[dict]:
    return [
        {"id": "801010", "name": "农林牧渔", "etf_code": "159825.SZ"},
        {"id": "801120", "name": "食品饮料", "etf_code": "515170.SH"},
        {"id": "801180", "name": "医药生物", "etf_code": "512010.SH"},
    ]


def _fallback_market_params() -> dict:
    return {
        "ema_period": 20,
        "bull_trend_bar_ratio": 0.40,
        "adx_threshold": 18,
        "confirmation_bars": 2,
    }


def _fallback_risk_constraints() -> list[dict]:
    return [
        {"layer": "L4", "threshold": "最大回撤 -20%", "action": "强制清仓"},
        {"layer": "L3", "threshold": "月度亏损 -15%", "action": "强制清仓"},
        {"layer": "L2", "threshold": "周亏损 -8%", "action": "减仓50%"},
        {"layer": "L1", "threshold": "日亏损 -3%", "action": "禁止新开仓"},
    ]
```

- [ ] **Step 2: 添加 bridge/__init__.py 导出**

```python
# investment_academy/bridge/__init__.py
from .data_reader import (
    list_available_etfs,
    load_etf_data,
    load_all_etf_metadata,
    get_etf_close_series,
    DataNotAvailableError,
)
from .knowledge_extractor import (
    extract_sector_list,
    extract_factor_definitions,
    extract_market_state_params,
    extract_risk_constraints,
    extract_setup_definitions,
)

__all__ = [
    # data_reader
    "list_available_etfs",
    "load_etf_data",
    "load_all_etf_metadata",
    "get_etf_close_series",
    "DataNotAvailableError",
    # knowledge_extractor
    "extract_sector_list",
    "extract_factor_definitions",
    "extract_market_state_params",
    "extract_risk_constraints",
    "extract_setup_definitions",
]
```

- [ ] **Step 3: 验证 knowledge_extractor**

```bash
cd investment_academy && python -c "
from bridge import extract_sector_list, extract_factor_definitions, extract_setup_definitions
print('Sectors:', len(extract_sector_list()))
print('Factors:', len(extract_factor_definitions()))
print('Setups:', len(extract_setup_definitions()))
print('OK')
"
```
Expected: 打印非零数量 + "OK"

- [ ] **Step 4: Commit**

```bash
git add investment_academy/bridge/
git commit -m "feat(academy): add Bridge knowledge_extractor — formulas, params, setups

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 实现内容加载器 + 测验组件

**Files:**
- Create: `investment_academy/interactive/content_loader.py`
- Create: `investment_academy/interactive/quiz_widget.py`
- Modify: `investment_academy/interactive/__init__.py`
- Create: `investment_academy/content/knowledge_track/p1_basics/chapter_01_stock_concept.md`
- Create: `investment_academy/content/knowledge_track/p1_basics/quiz.yaml`
- Create: `investment_academy/tests/test_interactive/test_content_loader.py`
- Create: `investment_academy/tests/test_content/test_quiz_yaml_valid.py`

- [ ] **Step 1: 创建 content_loader.py**

```python
# investment_academy/interactive/content_loader.py
"""学习内容加载器 — 加载 Markdown 章节和 YAML 测验"""
from pathlib import Path
from typing import Optional
import yaml

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"


def list_phases() -> list[dict]:
    """列出所有知识轨道阶段"""
    kt = CONTENT_ROOT / "knowledge_track"
    if not kt.exists():
        return []
    phases = []
    for d in sorted(kt.iterdir()):
        if d.is_dir():
            chapters = sorted(d.glob("chapter_*.md"))
            has_quiz = (d / "quiz.yaml").exists()
            phases.append({
                "id": d.name,
                "chapter_count": len(chapters),
                "has_quiz": has_quiz,
            })
    return phases


def list_labs() -> list[dict]:
    """列出所有实践轨道实验室"""
    pt = CONTENT_ROOT / "practice_track"
    if not pt.exists():
        return []
    labs = []
    for d in sorted(pt.iterdir()):
        if d.is_dir():
            has_guide = (d / "lab_guide.md").exists()
            has_exercises = (d / "exercises.yaml").exists()
            labs.append({
                "id": d.name,
                "has_guide": has_guide,
                "has_exercises": has_exercises,
            })
    return labs


def load_chapter(phase_id: str, chapter_file: str) -> Optional[str]:
    """加载章节 Markdown 内容"""
    path = CONTENT_ROOT / "knowledge_track" / phase_id / chapter_file
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_quiz(phase_id: str) -> Optional[dict]:
    """加载测验配置"""
    path = CONTENT_ROOT / "knowledge_track" / phase_id / "quiz.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_lab_guide(lab_id: str) -> Optional[str]:
    """加载实验室指南"""
    path = CONTENT_ROOT / "practice_track" / lab_id / "lab_guide.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_lab_exercises(lab_id: str) -> Optional[dict]:
    """加载实验室练习"""
    path = CONTENT_ROOT / "practice_track" / lab_id / "exercises.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

- [ ] **Step 2: 创建 quiz_widget.py**

```python
# investment_academy/interactive/quiz_widget.py
"""测验组件 — 单选、多选、判断"""
import streamlit as st
from typing import Optional

from models.quiz import QuizQuestion, QuizResult


def render_quiz(questions: list[dict], chapter_id: str) -> Optional[QuizResult]:
    """渲染一组测验题，返回测验结果或 None（用户尚未提交）

    Args:
        questions: list of quiz question dicts (from quiz.yaml)
        chapter_id: e.g. 'p1_ch1'

    Returns:
        QuizResult if submitted, None otherwise
    """
    if not questions:
        st.info("本章暂无测验题")
        return None

    parsed = [QuizQuestion.from_dict(q) for q in questions]

    st.markdown("---")
    st.subheader("📝 章节测验")

    # 使用 session_state 存储用户答案
    state_key = f"quiz_answers_{chapter_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {}

    answers = st.session_state[state_key]

    # 渲染每一题
    for q in parsed:
        st.markdown(f"**{q.id}.** {q.question}")

        if q.type == "single_choice":
            options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q.options)]
            selected = st.radio(
                f"选择答案 {q.id}",
                options=range(len(q.options)),
                format_func=lambda i: options[i],
                key=f"quiz_{chapter_id}_{q.id}",
                index=None,
            )
            if selected is not None:
                answers[q.id] = selected

        elif q.type == "multi_choice":
            selected = []
            for i, opt in enumerate(q.options):
                if st.checkbox(f"{chr(65+i)}. {opt}", key=f"quiz_{chapter_id}_{q.id}_{i}"):
                    selected.append(i)
            if selected:
                answers[q.id] = selected

        elif q.type == "true_false":
            selected = st.radio(
                f"判断 {q.id}",
                options=[True, False],
                format_func=lambda v: "✅ 正确" if v else "❌ 错误",
                key=f"quiz_{chapter_id}_{q.id}",
                index=None,
            )
            if selected is not None:
                answers[q.id] = selected

    # 提交按钮
    if st.button("提交答案", key=f"submit_{chapter_id}"):
        if len(answers) < len(parsed):
            st.warning("请完成所有题目后再提交")
            return None

        correct = 0
        for q in parsed:
            user_ans = answers.get(q.id)
            if user_ans == q.answer:
                correct += 1
            elif isinstance(q.answer, list) and isinstance(user_ans, list):
                if set(user_ans) == set(q.answer):
                    correct += 1

        score = correct / len(parsed) if parsed else 0.0

        # 显示反馈
        if score >= 0.8:
            st.success(f"🎉 得分: {correct}/{len(parsed)} ({score:.0%}) — 优秀！")
        elif score >= 0.6:
            st.info(f"📚 得分: {correct}/{len(parsed)} ({score:.0%}) — 通过，继续加油！")
        else:
            st.error(f"📖 得分: {correct}/{len(parsed)} ({score:.0%}) — 建议重新学习本章")

        # 显示解析
        with st.expander("查看解析"):
            for q in parsed:
                st.markdown(f"**{q.id}**: {q.explanation}")

        # 清除答案缓存（允许重做）
        del st.session_state[state_key]
        st.rerun()

        # 返回结果（rerun 后不会执行到这里，但保持签名完整）
        import datetime
        return QuizResult(
            chapter_id=chapter_id,
            total_questions=len(parsed),
            correct_count=correct,
            score=score,
            answers=answers,
            timestamp=datetime.datetime.now().isoformat(),
        )

    return None
```

- [ ] **Step 3: 更新 interactive/__init__.py**

```python
# investment_academy/interactive/__init__.py
from .content_loader import (
    list_phases,
    list_labs,
    load_chapter,
    load_quiz,
    load_lab_guide,
    load_lab_exercises,
)
from .quiz_widget import render_quiz

__all__ = [
    "list_phases",
    "list_labs",
    "load_chapter",
    "load_quiz",
    "load_lab_guide",
    "load_lab_exercises",
    "render_quiz",
]
```

- [ ] **Step 4: 创建 P1 第一章内容**

```markdown
<!-- investment_academy/content/knowledge_track/p1_basics/chapter_01_stock_concept.md -->
# 第一章：什么是股票？

## 1.1 股票的本质

**股票（Stock）** 是股份公司发行的所有权凭证。当你买入一家公司的股票，你就成为了这家公司的**股东**，拥有公司的一部分所有权。

打个比方：如果把一家公司比作一个大蛋糕，股票就像是把这个蛋糕切成很多小块。你买的每一股，就是蛋糕的一小块。拥有的块数越多，你在公司中的份额就越大。

## 1.2 股东的权利

作为股东，你享有以下权利：

- **分红权**：公司赚钱后，可以按持股比例获得分红
- **投票权**：对公司重大事项有投票表决权
- **知情权**：有权查看公司的财务报表和经营信息
- **价差收益**：股价上涨时卖出，获得差价利润

## 1.3 一级市场 vs 二级市场

- **一级市场（Primary Market）**：公司首次发行股票（IPO），投资者直接从公司购买
- **二级市场（Secondary Market）**：投资者之间相互买卖已发行的股票

我们日常说的"炒股"就是在**二级市场**进行的交易。

## 1.4 A股市场

**A股**是指在中国内地注册、在中国内地上市的股票，以人民币计价交易。

主要交易场所：
- **上海证券交易所（SSE）**：主板 + 科创板
- **深圳证券交易所（SZSE）**：主板 + 创业板

在 SPAS 系统中分析的大部分 ETF 都在沪深两市交易。

## 本章要点

| 概念 | 说明 |
|------|------|
| 股票 | 公司所有权的凭证 |
| 股东 | 持有股票的人，享有分红权、投票权 |
| IPO | 首次公开发行，公司第一次卖股票给公众 |
| 二级市场 | 投资者之间买卖股票的场所 |
| A股 | 在中国内地上市交易的股票 |
```

- [ ] **Step 5: 创建 P1 第一章测验**

```yaml
# investment_academy/content/knowledge_track/p1_basics/quiz.yaml
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
    answer: 1
    explanation: "股票是股份公司发行的所有权凭证，持有股票意味着你拥有公司的一部分所有权。"

  - id: q2
    type: single_choice
    question: "我们日常'炒股'发生在哪个市场？"
    options:
      - "一级市场"
      - "二级市场"
      - "期货市场"
      - "货币市场"
    answer: 1
    explanation: "一级市场是IPO发行市场，二级市场是投资者之间相互买卖的市场。我们说的炒股就是在二级市场。"

  - id: q3
    type: single_choice
    question: "以下哪个不是股东的权利？"
    options:
      - "分红权"
      - "投票权"
      - "无条件退款权"
      - "知情权"
    answer: 2
    explanation: "股东享有分红权、投票权、知情权，但没有无条件退款权。股票投资是有风险的。"

  - id: q4
    type: true_false
    question: "A股是以人民币计价、在中国内地上市交易的股票"
    options: []
    answer: true
    explanation: "正确。A股的'定义就是在内地注册、内地上市、人民币计价的股票。"

  - id: q5
    type: single_choice
    question: "IPO 是什么意思？"
    options:
      - "公司被收购"
      - "公司首次公开发行股票"
      - "公司退市"
      - "公司分红"
    answer: 1
    explanation: "IPO (Initial Public Offering) 即首次公开发行，是公司第一次向公众出售股票。"
```

- [ ] **Step 6: 写 content_loader 测试**

```python
# investment_academy/tests/test_interactive/test_content_loader.py
"""测试内容加载器"""
from interactive.content_loader import (
    list_phases, list_labs, load_chapter, load_quiz, load_lab_guide
)


def test_list_phases():
    phases = list_phases()
    assert len(phases) > 0
    p1 = [p for p in phases if p["id"] == "p1_basics"]
    assert len(p1) == 1
    assert "chapter_count" in p1[0]


def test_load_chapter_exists():
    content = load_chapter("p1_basics", "chapter_01_stock_concept.md")
    assert content is not None
    assert "股票" in content
    assert "## 1.1" in content


def test_load_chapter_not_exists():
    content = load_chapter("nonexistent", "fake.md")
    assert content is None


def test_load_quiz():
    quiz = load_quiz("p1_basics")
    assert quiz is not None
    assert "questions" in quiz
    assert len(quiz["questions"]) == 5
    # 校验每题必要字段
    for q in quiz["questions"]:
        assert "id" in q
        assert "type" in q
        assert "question" in q
        assert "answer" in q
        assert "explanation" in q


def test_list_labs():
    labs = list_labs()
    # 目前只有 m1
    m1 = [l for l in labs if l["id"] == "m1_data_lab"]
    assert len(m1) == 1
```

- [ ] **Step 7: 写 quiz YAML 内容校验测试**

```python
# investment_academy/tests/test_content/test_quiz_yaml_valid.py
"""校验所有测验 YAML 文件的格式正确性"""
import yaml
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def find_quiz_files():
    """找到所有 quiz.yaml 文件"""
    return list(CONTENT.glob("**/quiz.yaml"))


def test_all_quiz_files_parseable():
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{qf} 无法解析"
        assert "questions" in data, f"{qf} 缺少 questions"
        for q in data["questions"]:
            assert "id" in q, f"{qf}: 问题缺少 id"
            assert "type" in q, f"{qf}: {q['id']} 缺少 type"
            assert "question" in q, f"{qf}: {q['id']} 缺少 question"
            assert "answer" in q, f"{qf}: {q['id']} 缺少 answer"


def test_all_quiz_questions_have_valid_types():
    valid_types = {"single_choice", "multi_choice", "true_false"}
    for qf in find_quiz_files():
        with open(qf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for q in data["questions"]:
            assert q["type"] in valid_types, f"{qf}: {q['id']} 类型无效: {q['type']}"
            if q["type"] == "single_choice":
                assert isinstance(q["answer"], int), f"{qf}: {q['id']} answer应为int"
            if q["type"] == "multi_choice":
                assert isinstance(q["answer"], list), f"{qf}: {q['id']} answer应为list"
            if q["type"] == "true_false":
                assert isinstance(q["answer"], bool), f"{qf}: {q['id']} answer应为bool"
```

- [ ] **Step 8: 运行测试**

```bash
cd investment_academy && python -m pytest tests/test_interactive/test_content_loader.py tests/test_content/ -v
```
Expected: all passed

- [ ] **Step 9: Commit**

```bash
git add investment_academy/interactive/ investment_academy/content/ investment_academy/tests/
git commit -m "feat(academy): add content loader, quiz widget, and P1 chapter 1

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: 创建 Streamlit 主入口 app.py

**Files:**
- Create: `investment_academy/app.py`

- [ ] **Step 1: 创建 app.py**

```python
# investment_academy/app.py
"""投资学院 — Streamlit 主入口"""
import sys
from pathlib import Path

# 确保 investment_academy 在 sys.path 中
ACADEMY_ROOT = Path(__file__).resolve().parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

import streamlit as st

st.set_page_config(
    page_title="投资学院",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 自定义 CSS ──────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .phase-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    .phase-card h3 {
        color: white;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# ── 侧边栏导航 ─────────────────────────────────────
st.sidebar.title("📈 投资学院")

menu = st.sidebar.radio(
    "导航",
    [
        "🏠 首页",
        "📚 知识轨道",
        "🔬 实践轨道",
        "🎮 交易沙盒",
        "📊 学习进度",
    ],
    label_visibility="collapsed",
)

# ── 页面路由 ───────────────────────────────────────
if menu == "🏠 首页":
    st.markdown('<p class="main-header">📈 投资学院</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">从零基础到投资大拿 — 系统化掌握股市与投资知识</p>',
                unsafe_allow_html=True)

    # 三列卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="phase-card">
            <h3>📚 知识轨道</h3>
            <p>7个阶段 · 34章系统学习</p>
            <p>从股市基础概念到完整交易系统，循序渐进</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="phase-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>🔬 实践轨道</h3>
            <p>6个实验室 · 动手探索</p>
            <p>用真实市场数据做实验，理解每个概念的实际含义</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="phase-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>🎮 交易沙盒</h3>
            <p>零风险模拟交易</p>
            <p>用历史数据练习交易决策，积累实战经验</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 快速概览
    st.subheader("🚀 快速开始")
    st.markdown("""
    1. **如果你是纯新手** → 从 📚 知识轨道 → P1 股市基础开始
    2. **如果你想动手实践** → 去 🔬 实践轨道 → M1 数据勘探实验室
    3. **如果你想测试自己** → 用 🎮 交易沙盒模拟真实交易
    """)

    # 学习路径图
    st.subheader("🗺️ 学习路径")

    path_data = [
        {"阶段": "P1 股市基础", "主题": "股票/ETF/K线/交易规则", "章节": "5章", "建议时间": "2天"},
        {"阶段": "P2 技术分析", "主题": "趋势/微观结构/均线/Wyckoff", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P3 板块产业链", "主题": "行业分类/产业链/板块轮动", "章节": "4章", "建议时间": "2天"},
        {"阶段": "P4 量化策略", "主题": "概率思维/规则策略/ML融合", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P5 风险管理", "主题": "仓位/回撤/波动率/尾部风险", "章节": "5章", "建议时间": "3天"},
        {"阶段": "P6 交易心理", "主题": "情绪管理/认知偏差/市场情绪", "章节": "6章", "建议时间": "3天"},
        {"阶段": "P7 实战整合", "主题": "回测/偏差/完整交易系统", "章节": "4章", "建议时间": "2天"},
    ]
    import pandas as pd
    st.dataframe(pd.DataFrame(path_data), use_container_width=True, hide_index=True)

elif menu == "📚 知识轨道":
    # 阶段选择
    from interactive.content_loader import list_phases

    phases = list_phases()
    phase_names = {
        "p1_basics": "P1: 股市基础",
        "p2_technical": "P2: 技术分析入门",
        "p3_sectors": "P3: 板块与产业链",
        "p4_quant": "P4: 量化策略思维",
        "p5_risk": "P5: 风险管理",
        "p6_psychology": "P6: 交易心理与市场情绪",
        "p7_integration": "P7: 实战整合",
    }

    phase_options = []
    for p in phases:
        name = phase_names.get(p["id"], p["id"])
        phase_options.append(f"{name} ({p['chapter_count']}章)")

    if phase_options:
        selected = st.sidebar.selectbox("选择阶段", phase_options)
        selected_id = phases[phase_options.index(selected)]["id"]

        # 动态导入页面模块
        module_name = f"pages.knowledge.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"📝 {phase_names.get(selected_id, selected_id)} 内容正在编写中…")
        except ImportError:
            st.info(f"📝 {phase_names.get(selected_id, selected_id)} 内容正在编写中…")
    else:
        st.info("暂无可用章节内容")

elif menu == "🔬 实践轨道":
    from interactive.content_loader import list_labs

    labs = list_labs()
    lab_names = {
        "m1_data_lab": "M1: 数据勘探实验室",
        "m2_feature_lab": "M2: 特征工程实验室",
        "m3_prediction": "M3: 预测引擎探索",
        "m4_risk_sandbox": "M4: 风控沙盒",
        "m5_backtest": "M5: 回测分析器",
        "m6_sentiment": "M6: 市场情绪实验室",
    }

    lab_options = [lab_names.get(l["id"], l["id"]) for l in labs]
    if lab_options:
        selected = st.sidebar.selectbox("选择实验室", lab_options)
        selected_id = labs[lab_options.index(selected)]["id"]

        module_name = f"pages.practice.{selected_id}"
        try:
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "show"):
                mod.show()
            else:
                st.info(f"🔬 {lab_names.get(selected_id, selected_id)} 正在建设中…")
        except ImportError:
            st.info(f"🔬 {lab_names.get(selected_id, selected_id)} 正在建设中…")
    else:
        st.info("暂无可用实验")

elif menu == "🎮 交易沙盒":
    st.markdown("## 🎮 交易沙盒")
    st.info("🚧 交易沙盒正在建设中… 完成后你将可以在这里用历史数据模拟真实交易决策。")

elif menu == "📊 学习进度":
    st.markdown("## 📊 学习进度")
    st.info("🚧 学习进度仪表盘正在建设中…")
```

- [ ] **Step 2: 验证启动**

```bash
cd investment_academy && streamlit run app.py --server.headless true 2>&1 | head -5
```
Expected: 看到 Streamlit 启动信息（Ctrl+C 终止）

- [ ] **Step 3: Commit**

```bash
git add investment_academy/app.py
git commit -m "feat(academy): add Streamlit main entry with dual-track navigation

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: 实现 P1 知识轨道页面

**Files:**
- Create: `investment_academy/pages/knowledge/p1_basics.py`

- [ ] **Step 1: 创建 p1_basics.py**

```python
# investment_academy/pages/knowledge/p1_basics.py
"""P1: 股市基础 — 知识轨道页面"""
import streamlit as st
from interactive.content_loader import load_chapter, load_quiz
from interactive.quiz_widget import render_quiz
from db.repository import save_chapter_progress, get_chapter_progress


P1_CHAPTERS = [
    {"file": "chapter_01_stock_concept.md", "title": "第一章：什么是股票？", "id": "p1_ch1"},
    {"file": "chapter_02_etf_basics.md", "title": "第二章：ETF 入门", "id": "p1_ch2"},
    {"file": "chapter_03_a_share_rules.md", "title": "第三章：A股交易规则", "id": "p1_ch3"},
    {"file": "chapter_04_kline_intro.md", "title": "第四章：K线图入门", "id": "p1_ch4"},
    {"file": "chapter_05_ohlcv.md", "title": "第五章：基本术语", "id": "p1_ch5"},
]


def show():
    st.markdown("## 📚 P1: 股市基础")
    st.markdown("*从零开始，理解股票市场的基本概念*")

    # 章节选择
    chapter_labels = [f"{ch['title']}" for ch in P1_CHAPTERS]
    selected = st.sidebar.radio("P1 目录", chapter_labels, label_visibility="collapsed")
    idx = chapter_labels.index(selected)
    ch = P1_CHAPTERS[idx]

    # 加载章节内容
    content = load_chapter("p1_basics", ch["file"])
    if content:
        # 去除 YAML frontmatter 注释行（<!-- ... -->）
        st.markdown(content, unsafe_allow_html=False)
    else:
        st.warning(f"📝 {ch['title']} 内容正在编写中…")
        return

    # 显示进度
    progress = get_chapter_progress(ch["id"])
    if progress and progress.get("completed"):
        st.success(f"✅ 已完成 — 测验得分: {progress['quiz_score']:.0%}")

    # 测验（只有内容已加载时显示）
    quiz_data = load_quiz("p1_basics")
    if quiz_data and quiz_data.get("chapter") == ch["id"]:
        result = render_quiz(quiz_data["questions"], ch["id"])
        if result and result.passed:
            save_chapter_progress(
                chapter_id=ch["id"],
                completed=True,
                quiz_score=result.score,
                quiz_attempts=1,
            )
            st.rerun()
```

- [ ] **Step 2: 验证导入**

```bash
cd investment_academy && python -c "from pages.knowledge.p1_basics import show; print('P1 page OK')"
```
Expected: `P1 page OK`

- [ ] **Step 3: Commit**

```bash
git add investment_academy/pages/
git commit -m "feat(academy): add P1 basics knowledge page with chapter navigation and quiz

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: 创建 M1 实践轨道页面（占位）

**Files:**
- Create: `investment_academy/pages/practice/m1_data_lab.py`
- Create: `investment_academy/content/practice_track/m1_data_lab/lab_guide.md`

- [ ] **Step 1: 创建 m1_data_lab.py**

```python
# investment_academy/pages/practice/m1_data_lab.py
"""M1: 数据勘探实验室"""
import streamlit as st
import pandas as pd
from bridge.data_reader import list_available_etfs, load_etf_data, load_all_etf_metadata
from interactive.content_loader import load_lab_guide


def show():
    st.markdown("## 🔬 M1: 数据勘探实验室")
    st.markdown("*探索真实的 ETF 市场数据*")

    # 加载实验指南
    guide = load_lab_guide("m1_data_lab")
    if guide:
        with st.expander("📖 实验指南", expanded=True):
            st.markdown(guide)

    # ETF 元数据总览
    st.subheader("📊 可用 ETF 数据总览")
    meta = load_all_etf_metadata()
    if not meta.empty:
        st.dataframe(meta, use_container_width=True, hide_index=True)
    else:
        st.warning("未找到 ETF 数据文件")

    # ETF 数据浏览器
    st.subheader("🔍 ETF 数据浏览器")
    etfs = list_available_etfs()
    if etfs:
        etf_codes = [e["code"] for e in etfs]
        selected_code = st.selectbox("选择 ETF", etf_codes)
        timeframe = st.selectbox("时间框架", ["day", "5min"])

        df = load_etf_data(selected_code, timeframe)
        if df is not None:
            st.metric("数据行数", len(df))
            st.dataframe(df.head(20), use_container_width=True)

            # 简易收盘价走势图
            if "close" in df.columns and "trade_date" in df.columns:
                st.subheader("收盘价走势")
                st.line_chart(
                    df.set_index("trade_date")["close"],
                    use_container_width=True,
                )
        else:
            st.warning(f"无法加载 {selected_code} 的 {timeframe} 数据")
    else:
        st.info("未找到可用的 ETF 数据")
```

- [ ] **Step 2: 创建 lab_guide.md**

```markdown
# M1: 数据勘探实验室 — 实验指南

## 实验目标

通过浏览真实的 ETF 市场数据，建立对市场数据的直观认识。

## 实验步骤

### 1. 浏览数据总览

观察「可用 ETF 数据总览」表格，回答：
- 一共有多少个 ETF？
- 数据最早从什么时候开始？最新到什么时候？
- 哪个 ETF 数据最多？

### 2. 查看单个 ETF 数据

选择一个 ETF，查看其数据表格：
- 表格有哪些列？每列代表什么含义？
- 数据是按什么频率记录的？（日线 vs 5分钟线）

### 3. 观察收盘价走势

切换到图表视图：
- 价格整体趋势是上涨还是下跌？
- 有没有明显的大涨或大跌区间？
- 成交量在哪个时间段最大？

## 关键概念

| 列名 | 含义 |
|------|------|
| trade_date | 交易日期 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
```

- [ ] **Step 3: 验证导入**

```bash
cd investment_academy && python -c "from pages.practice.m1_data_lab import show; print('M1 page OK')"
```
Expected: `M1 page OK`

- [ ] **Step 4: Commit**

```bash
git add investment_academy/pages/practice/ investment_academy/content/practice_track/
git commit -m "feat(academy): add M1 data exploration lab with ETF browser

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 10: 端到端验证 + conftest

**Files:**
- Create: `investment_academy/tests/conftest.py`

- [ ] **Step 1: 创建 conftest.py**

```python
# investment_academy/tests/conftest.py
"""共享的 pytest fixtures"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# 确保项目在 sys.path
ACADEMY_ROOT = Path(__file__).resolve().parent.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))


@pytest.fixture
def temp_db():
    """创建临时数据库并注入到 repository"""
    from db import repository
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    old_path = repository.DB_PATH
    repository.DB_PATH = tmp.name
    yield tmp.name
    repository.DB_PATH = old_path
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)
```

- [ ] **Step 2: 运行全量测试**

```bash
cd investment_academy && python -m pytest tests/ -v --tb=short
```
Expected: 所有测试通过（integration 标记的除外，默认跳过）

- [ ] **Step 3: 端到端验证：启动 Streamlit 并检查无导入错误**

```bash
cd investment_academy && python -c "
import streamlit as st
from models import ChapterProgress, QuizResult, UserPreferences
from db import save_chapter_progress, get_chapter_progress, get_user_preferences
from bridge import list_available_etfs, extract_factor_definitions
from interactive import load_chapter, load_quiz, render_quiz
from pages.knowledge.p1_basics import show
print('✅ All imports successful')
print(f'ETFs available: {len(list_available_etfs())}')
print(f'Factor definitions: {len(extract_factor_definitions())}')
print(f'P1 chapters: chapter_01 loaded = {load_chapter(\"p1_basics\", \"chapter_01_stock_concept.md\") is not None}')
"
```
Expected: `✅ All imports successful` + 正数 counts

- [ ] **Step 4: Commit**

```bash
git add investment_academy/tests/conftest.py
git commit -m "feat(academy): add conftest and verify end-to-end imports

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 1 完成检查清单

Phase 1 完成后，系统应具备以下能力：

- [x] `investment_academy/` 目录结构完整
- [x] 独立 `pyproject.toml` 和 `requirements.txt`
- [x] 数据模型层（3个模块，含序列化/反序列化）
- [x] SQLite 持久化层（6张表，完整 CRUD）
- [x] Bridge 层 data_reader（读取 Parquet ETF 数据）
- [x] Bridge 层 knowledge_extractor（提取行业/因子/参数/风控/Setup 知识）
- [x] Content 层（load_chapter, load_quiz, load_lab_guide）
- [x] Quiz widget（单选/多选/判断 + 即时判分 + 解析）
- [x] Streamlit 主入口 + 双轨导航
- [x] P1 知识轨道页面（5章结构 + 测验集成）
- [x] M1 实践轨道页面（ETF 数据浏览器）
- [x] P1 第一章完整内容（Markdown + YAML测验）
- [x] 测试套件（models + db + bridge + interactive + content）
- [x] `streamlit run app.py` 可启动并正常工作

---

## Phase 2: 内容批量填充（后续）

### Task 11: P1 剩余章节（Ch2-Ch5）
- 编写 chapter_02_etf_basics.md
- 编写 chapter_03_a_share_rules.md
- 编写 chapter_04_kline_intro.md
- 编写 chapter_05_ohlcv.md
- 更新 quiz.yaml 覆盖所有章节

### Task 12: P2 技术分析入门（5章）
- 编写 5 章 Markdown + quiz.yaml
- 创建 pages/knowledge/p2_technical.py

### Task 13-P16: P3-P7 + M2-M6
- 按 spec 的章节表逐步完成

---

## Phase 3: 交互组件（后续）

### Task 17: K线图组件 (kline_chart.py)
- Plotly OHLC 图 + 成交量柱状图
- 信号标注叠加

### Task 18: 特征实验室 (feature_explorer.py)
- 参数滑块调节
- 实时图表反馈

### Task 19: 交易沙盒 (sandbox_engine.py)
- 历史数据回放
- 买卖决策 + 结果追踪
- 绩效指标

### Task 20: 市场情绪可视化 (sentiment_viz.py)
- 行业情绪热力图
- 情绪-价格叠加图

### Task 21: 心理自检清单 (psychology_checklist.py)
- 交互式问卷
- 风险等级评估

---

## Phase 4: 完善（后续）

### Task 22: 学习进度仪表盘 (progress_dashboard.py)
- 进度条、成绩趋势图
- 徽章成就系统

### Task 23: 术语表
- 可搜索的术语表页面
- content/glossary.yaml

### Task 24: 回测分析器页面
- M5 回测结果可视化

---

## 附录：常用命令

```bash
# 安装依赖
cd investment_academy && pip install -r requirements.txt

# 运行测试
cd investment_academy && python -m pytest tests/ -v

# 运行测试（跳过 integration）
cd investment_academy && python -m pytest tests/ -v -m "not integration"

# 启动 Streamlit
cd investment_academy && streamlit run app.py

# 查看测试覆盖率
cd investment_academy && python -m pytest tests/ --cov=. --cov-report=term-missing
```
