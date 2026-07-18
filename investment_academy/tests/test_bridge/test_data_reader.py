"""测试 data_reader"""
import pytest
from core.bridge.data_reader import list_available_etfs, load_etf_data, load_all_etf_metadata


@pytest.mark.integration
def test_list_available_etfs():
    """项目中已知至少有 ETF 数据"""
    etfs = list_available_etfs()
    assert len(etfs) > 0
    for etf in etfs:
        assert "code" in etf
        assert "market" in etf
        assert etf["market"] in ("SH", "SZ")


@pytest.mark.integration
def test_load_etf_data_known():
    """加载已知存在的 ETF"""
    df = load_etf_data("510300.SH", "day")
    assert df is not None
    assert len(df) > 100
    assert "close" in df.columns or "trade_date" in df.columns


@pytest.mark.integration
def test_load_etf_data_nonexistent():
    """加载不存在的 ETF 返回 None"""
    df = load_etf_data("999999.SZ", "day")
    assert df is None


@pytest.mark.integration
def test_load_all_etf_metadata():
    meta = load_all_etf_metadata()
    assert len(meta) > 0
    assert "code" in meta.columns


def test_list_etfs_no_data_dir(monkeypatch, tmp_path):
    """SPAS_DATA_DIR 不存在时返回空列表"""
    from core.bridge import data_reader
    monkeypatch.setattr(data_reader, "SPAS_DATA_DIR", tmp_path / "nonexistent")
    etfs = data_reader.list_available_etfs()
    assert etfs == []
