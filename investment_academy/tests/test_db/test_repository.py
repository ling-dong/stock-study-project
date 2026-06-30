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
    os.unlink(db_path)


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
