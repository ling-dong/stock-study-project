"""SPAS API 集成测试 — 验证新版核心端点"""
import pytest
from fastapi.testclient import TestClient

from src.signals.api import create_app
from src.signals.service import SPASService


@pytest.fixture
def client():
    service = SPASService()
    app = create_app(service)
    return TestClient(app)


class TestSPASAPI:
    def test_system_status(self, client):
        r = client.get("/api/spas/system/status")
        assert r.status_code == 200
        data = r.json()
        assert "version" in data
        assert "data_dir" in data

    def test_market_etfs(self, client):
        r = client.get("/api/spas/market/etfs")
        assert r.status_code == 200
        etfs = r.json()
        assert len(etfs) > 0
        assert all("code" in e and "market" in e for e in etfs)

    def test_market_etfs_meta(self, client):
        r = client.get("/api/spas/market/etfs/meta")
        assert r.status_code == 200
        meta = r.json()
        assert len(meta) > 0
        assert all("code" in m and "rows" in m and "start_date" in m for m in meta)

    def test_ohlcv(self, client):
        r = client.get("/api/spas/market/etf/512480.SH/ohlcv?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["code"] == "512480.SH"
        assert len(data["bars"]) == 5
        assert all("open" in b and "high" in b and "low" in b and "close" in b for b in data["bars"])

    def test_ohlcv_not_found(self, client):
        r = client.get("/api/spas/market/etf/INVALID.CODE/ohlcv")
        assert r.status_code == 404

    def test_signal(self, client):
        r = client.get("/api/spas/signal/512480.SH")
        assert r.status_code == 200
        data = r.json()
        assert data["symbol"] == "512480.SH"
        assert "market_state" in data
        assert "setup_summary" in data
        assert "prediction" in data
        assert "current_price" in data

    def test_signal_not_found(self, client):
        r = client.get("/api/spas/signal/INVALID.CODE")
        assert r.status_code == 404

    def test_legacy_endpoints(self, client):
        r = client.get("/system/status")
        assert r.status_code == 200
        r = client.get("/system/version")
        assert r.status_code == 200
        r = client.get("/signals/latest")
        assert r.status_code == 200
        r = client.get("/signals/history?limit=5")
        assert r.status_code == 200
