"""后端 API 集成测试 — 使用 FastAPI TestClient"""
import sys
from pathlib import Path

ACADEMY_ROOT = Path(__file__).resolve().parent.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# ── Health ─────────────────────────────────────────────

def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


# ── Content ────────────────────────────────────────────

def test_list_phases():
    resp = client.get("/api/content/phases")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(p["id"] == "p1_basics" for p in data)


def test_list_labs():
    resp = client.get("/api/content/labs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(l["id"] == "m1_data_lab" for l in data)


def test_get_chapter():
    resp = client.get("/api/content/chapter/p1_basics/chapter_01_stock_concept.md")
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert "股票" in data["content"]


def test_get_chapter_404():
    resp = client.get("/api/content/chapter/p1_basics/nonexistent.md")
    assert resp.status_code == 404


def test_get_quiz_all():
    """不传 chapter_id 返回全部章节"""
    resp = client.get("/api/content/quiz/p1_basics")
    assert resp.status_code == 200
    data = resp.json()
    assert "chapters" in data
    assert "p1_ch1" in data["chapters"]


def test_get_quiz_single_chapter():
    """传 chapter_id 只返回单章"""
    resp = client.get("/api/content/quiz/p1_basics?chapter_id=p1_ch1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapter"] == "p1_ch1"
    assert len(data["questions"]) == 5


def test_get_quiz_nonexistent_chapter():
    """不存在的章节返回 None → 404"""
    resp = client.get("/api/content/quiz/p1_basics?chapter_id=nonexistent")
    assert resp.status_code == 404


def test_get_lab():
    resp = client.get("/api/content/lab/m1_data_lab")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("guide") is not None


# ── Quiz ───────────────────────────────────────────────

def test_submit_quiz_all_correct():
    resp = client.post("/api/quiz/submit", json={
        "phase_id": "p1_basics",
        "chapter_id": "p1_ch1",
        "answers": {"q1": 1, "q2": 1, "q3": 2, "q4": True, "q5": 1},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert "correct_count" in data
    assert "total" in data
    assert data["total"] == 5


def test_submit_quiz_all_wrong():
    resp = client.post("/api/quiz/submit", json={
        "phase_id": "p1_basics",
        "chapter_id": "p1_ch1",
        "answers": {"q1": 0, "q2": 0, "q3": 0, "q4": False, "q5": 0},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["correct_count"] == 0
    assert data["passed"] is False


def test_submit_quiz_nonexistent_phase():
    resp = client.post("/api/quiz/submit", json={
        "phase_id": "nonexistent",
        "chapter_id": "p1_ch1",
        "answers": {},
    })
    assert resp.status_code == 404


# ── Progress ───────────────────────────────────────────

def test_progress_list():
    resp = client.get("/api/progress")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_progress_crud():
    """完整的 CRUD 流程"""
    # Get (可能 404)
    resp = client.get("/api/progress/p1_test")
    initial_status = resp.status_code

    # Create/Update
    resp = client.post("/api/progress/p1_test", json={
        "completed": True,
        "quiz_score": 0.8,
        "quiz_attempts": 1,
        "time_spent_seconds": 300,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapter_id"] == "p1_test"
    assert data["completed"] in (True, 1)  # SQLite stores bool as 0/1


# ── Market ─────────────────────────────────────────────

def test_list_etfs():
    resp = client.get("/api/market/etfs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "code" in data[0]


def test_etf_metadata():
    resp = client.get("/api/market/etfs/meta")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_etf_name():
    resp = client.get("/api/market/etf/510300.SH/name")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "510300.SH"
    assert "display_name" in data


def test_etf_ohlcv():
    resp = client.get("/api/market/etf/510300.SH/ohlcv?tf=day&limit=10")
    # 如果 SPAS 数据存在则 200，否则 404
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.json()
        assert data["code"] == "510300.SH"
        assert len(data["bars"]) <= 10


# ── Knowledge ──────────────────────────────────────────

def test_knowledge_sectors():
    resp = client.get("/api/knowledge/sectors")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_knowledge_factors():
    resp = client.get("/api/knowledge/factors")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 6  # 6 维特征
    assert data[0]["name"] == "body_ratio"


def test_knowledge_market_params():
    resp = client.get("/api/knowledge/market-params")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ema_period"] == 20


def test_knowledge_risk_constraints():
    resp = client.get("/api/knowledge/risk-constraints")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(c["layer"] == "L1" for c in data)


def test_knowledge_setups():
    resp = client.get("/api/knowledge/setups")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(s["name"] == "H2" for s in data)


# ── Sandbox ────────────────────────────────────────────

def test_sandbox_init():
    resp = client.post("/api/sandbox/init", json={
        "etf_code": "510300.SH",
        "timeframe": "day",
        "initial_cash": 100000.0,
    })
    # 如果 ETF 数据存在则 200，否则 404
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.json()
        assert "session_id" in data
        return data["session_id"]
    return None


def test_sandbox_full_flow():
    """完整沙盒流程"""
    # Init
    resp = client.post("/api/sandbox/init", json={
        "etf_code": "510300.SH",
        "timeframe": "day",
        "initial_cash": 100000.0,
    })
    if resp.status_code != 200:
        return  # SPAS 数据不可用
    sid = resp.json()["session_id"]

    # State
    resp = client.get(f"/api/sandbox/{sid}/state")
    assert resp.status_code == 200
    state = resp.json()
    assert state["cash"] == 100000.0
    assert state["shares"] == 0
    assert state["is_done"] is False

    # Bar
    resp = client.get(f"/api/sandbox/{sid}/bar")
    assert resp.status_code == 200
    bar = resp.json()
    assert "close" in bar

    # Can buy
    resp = client.get(f"/api/sandbox/{sid}/can-buy")
    assert resp.status_code == 200
    assert resp.json()["can"] in (True, False)

    # Buy
    resp = client.post(f"/api/sandbox/{sid}/buy", json={"shares": 100, "reason": "test"})
    if resp.status_code == 200:
        trade = resp.json()["trade"]
        assert trade["action"] == "buy"
        assert trade["shares"] == 100

    # Portfolio
    resp = client.get(f"/api/sandbox/{sid}/portfolio")
    assert resp.status_code == 200

    # Sell
    resp = client.post(f"/api/sandbox/{sid}/sell", json={"shares": 0, "reason": "test"})
    if resp.status_code == 200 and resp.json().get("trade"):
        trade = resp.json()["trade"]
        assert trade["action"] == "sell"

    # Performance (after selling everything)
    resp = client.get(f"/api/sandbox/{sid}/performance")
    assert resp.status_code == 200

    # Invalid session
    resp = client.get("/api/sandbox/fake123/state")
    assert resp.status_code == 404


# ── User ───────────────────────────────────────────────

def test_user_preferences_get():
    resp = client.get("/api/user/preferences")
    assert resp.status_code == 200
    data = resp.json()
    assert "current_phase" in data


def test_user_preferences_put():
    resp = client.put("/api/user/preferences", json={
        "current_phase": "p2",
        "preferred_timeframe": "5min",
        "sandbox_balance": 50000.0,
        "achievements": ["first_quiz"],
        "risk_profile": "aggressive",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_phase"] == "p2"
    assert data["risk_profile"] == "aggressive"


def test_psychology_check():
    resp = client.post("/api/user/psychology-check", json={
        "scores": {"calm": 4, "focus": 3},
        "overall_risk_level": "green",
        "proceeded_to_trade": True,
        "self_notes": "感觉良好",
    })
    assert resp.status_code == 200
    assert resp.json()["id"] > 0


def test_psychology_history():
    resp = client.get("/api/user/psychology-history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_journal_crud():
    # Create
    resp = client.post("/api/user/journal", json={
        "date": "2026-07-01",
        "setup_type": "H2",
        "entry_reason": "双底确认",
        "exit_reason": "到达目标价",
        "pnl_pct": 2.35,
        "emotional_state": "冷静",
        "lesson_learned": "耐心等待确认信号",
        "mistake_flag": False,
    })
    assert resp.status_code == 200
    assert resp.json()["id"] > 0

    # List
    resp = client.get("/api/user/journal")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
