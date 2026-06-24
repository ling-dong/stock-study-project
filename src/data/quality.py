"""§4.1.4 数据质量监控 — 完整性/时效性/异常值"""
import pandas as pd


class DataQualityMonitor:
    def __init__(self, max_missing_rate: float = 0.05, max_delay_p99_ms: float = 30000,
                 max_bar_change_pct: float = 10.0, max_volume_multiplier: float = 5.0):
        self.max_missing_rate = max_missing_rate
        self.max_delay_p99_ms = max_delay_p99_ms
        self.max_bar_change_pct = max_bar_change_pct
        self.max_volume_multiplier = max_volume_multiplier

    def check_completeness(self, df: pd.DataFrame, expected_count: int) -> tuple:
        actual = len(df)
        rate = 1.0 - (actual / expected_count) if expected_count > 0 else 1.0
        return rate <= self.max_missing_rate, rate

    def check_timeliness(self, latencies_ms: list) -> dict:
        if not latencies_ms:
            return {"p50": 0, "p99": 0, "p999": 0, "pass": True}
        sorted_lat = sorted(latencies_ms)
        p50 = sorted_lat[len(sorted_lat) // 2]
        p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
        p999 = sorted_lat[int(len(sorted_lat) * 0.999)]
        return {"p50": p50, "p99": p99, "p999": p999, "pass": p99 <= self.max_delay_p99_ms}

    def detect_anomalies(self, df: pd.DataFrame, avg_volume_20d: float) -> pd.Series:
        anomalies = pd.Series(False, index=df.index)
        if "close" in df.columns and "open" in df.columns:
            change_pct = abs((df["close"] - df["open"]) / df["open"] * 100)
            anomalies |= change_pct > self.max_bar_change_pct
        if "volume" in df.columns and avg_volume_20d > 0:
            anomalies |= df["volume"] > avg_volume_20d * self.max_volume_multiplier
        return anomalies
