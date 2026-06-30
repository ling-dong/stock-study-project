"""SQLite 数据访问层 — 每个函数独立、可单独测试"""
import sqlite3
import json
import os
from typing import Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
DB_PATH = os.path.join(DB_DIR, "academy.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


def _get_conn(db_path: Optional[str] = None) -> sqlite3.Connection:
    """获取数据库连接并初始化 schema"""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


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
