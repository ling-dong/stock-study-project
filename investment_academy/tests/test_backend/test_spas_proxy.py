"""后端 routers/spas.py 与 manual_analysis.py 测试"""
import sys
from pathlib import Path

ACADEMY_ROOT = Path(__file__).resolve().parent.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestManualAnalysis:
    def test_manual_analysis_system_info(self):
        resp = client.get("/api/manual-analysis/system-info")
        assert resp.status_code == 200
        data = resp.json()
        assert "etf_count" in data
        assert "data_latest_date" in data

    def test_manual_analysis_history(self):
        resp = client.get("/api/manual-analysis/history")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_manual_analysis_analysis_not_found(self):
        """不存在的 ETF 返回 404"""
        resp = client.post("/api/manual-analysis/analysis/NONEXIST.CODE", json={
            "current_price": 1.0, "adx": 25, "plus_di": 30, "minus_di": 20,
            "atr": 0.05, "asi_value": 100, "asi_direction": "up",
            "dif": 0.02, "dea": 0.01, "macd_bar": "red_increasing",
            "rsi": 50, "wr": 50, "volume_ratio": 1.0, "turnover_rate": 2.0,
            "obv_direction": "up", "market_trend": "bull", "market_adx": 25,
            "rr_ratio": 2.0, "max_loss_pct": 5.0,
            "psychology_answers": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        })
        assert resp.status_code == 404


class TestSPASProxy:
    def test_spas_proxy_without_spas_api_running(self):
        """SPAS API 未启动时，代理返回 503"""
        resp = client.get("/api/spas/system/status")
        # 如果 SPAS API 未运行，返回 503
        assert resp.status_code in (503, 200)
