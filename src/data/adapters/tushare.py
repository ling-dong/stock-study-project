"""Tushare Pro适配器 — 主力数据源(第二优先级) §7.2.1"""
from datetime import datetime, timedelta
from typing import Optional
import logging
import pandas as pd
from src.data.adapters.base import DataAdapter

logger = logging.getLogger(__name__)


class TushareAdapter(DataAdapter):
    """Tushare Pro数据适配器 — §7.2.1

    分钟级数据不提供复权，需配合PriceAdjuster使用。
    频率限制: 150次/分钟。
    """
    source_name = "tushare"

    FREQ_MAP = {
        "5min": "5min",
        "15min": "15min",
        "60min": "60min",
        "day": "D",
    }

    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None):
        self.token = token or self._token_from_env()
        self.api_url = api_url or "https://ts.gyzcloud.top/api"
        self._pro = None
        self._healthy = True

        if self.token:
            self._init_pro()
        else:
            self._healthy = False
            logger.warning("TUSHARE_TOKEN 未设置，Tushare 数据源不可用")

    @staticmethod
    def _token_from_env() -> Optional[str]:
        import os
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key == "TUSHARE_TOKEN" and key not in os.environ:
                        os.environ[key] = value
        return os.environ.get("TUSHARE_TOKEN")

    def _init_pro(self):
        try:
            import tushare as ts
            ts.set_token(self.token)
            self._pro = ts.pro_api()
            if self.api_url:
                self._pro._DataApi__http_url = self.api_url
            self._healthy = True
        except Exception as e:
            self._healthy = False
            self._pro = None

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """获取K线数据 — §7.2.1

        日线: 调用 pro_api.daily()
        分钟: 调用 pro_api.pro_bar() (返回数据不含复权)
        """
        if self._pro is None:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

        try:
            start_str = start.strftime("%Y%m%d") if start else None
            end_str = end.strftime("%Y%m%d") if end else (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

            # 解析symbol: "510300.SH" → ts_code="510300.SH"
            ts_code = self._normalize_symbol(symbol)

            if freq == "day":
                df = self._fetch_daily(ts_code, start_str, end_str)
            else:
                tf = self.FREQ_MAP.get(freq, "5min")
                df = self._fetch_minute(ts_code, tf, start_str, end_str)

            if df is None or df.empty:
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

            df = self._standardize_columns(df)
            return df

        except Exception as e:
            self._healthy = False
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化标的代码"""
        return symbol.upper().replace(".SZ", ".SZ").replace(".SH", ".SH")

    def _fetch_daily(self, ts_code: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """获取日线数据

        ETF(51xxxx/15xxxx)用 fund_daily，普通股票用 daily。
        先尝试 fund_daily，失败回退到 daily。
        """
        is_etf = (ts_code.startswith("51") or ts_code.startswith("15")
                  or ts_code.startswith("58") or ts_code.startswith("56"))

        # 策略1: fund_daily (ETF专用)
        if is_etf and hasattr(self._pro, 'fund_daily'):
            try:
                df = self._pro.fund_daily(
                    ts_code=ts_code,
                    start_date=start,
                    end_date=end,
                    fields="ts_code,trade_date,open,high,low,close,vol,amount",
                )
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                logger.debug(f"fund_daily failed for {ts_code}: {e}")

        # 策略2: pro_bar (通用接口)
        if hasattr(self._pro, 'pro_bar'):
            try:
                df = self._pro.pro_bar(
                    ts_code=ts_code,
                    start_date=start,
                    end_date=end,
                    freq="D",
                    asset="FD" if is_etf else "E",
                    fields="ts_code,trade_date,open,high,low,close,vol,amount",
                )
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                logger.debug(f"pro_bar failed for {ts_code}: {e}")

        # 策略3: daily (股票接口，ETF可能失败)
        try:
            df = self._pro.daily(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                fields="ts_code,trade_date,open,high,low,close,vol,amount",
            )
            return df
        except Exception as e:
            logger.debug(f"daily failed for {ts_code}: {e}")
            return None

    def _fetch_minute(self, ts_code: str, freq: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """获取分钟数据（不含复权）"""
        try:
            df = self._pro.pro_bar(
                ts_code=ts_code,
                freq=freq,
                start_date=start.replace("-", "") if start else None,
                end_date=end.replace("-", "") if end else None,
                asset="E",  # ETF
            )
            if df is None:
                # 回退: asset='FD' 基金
                df = self._pro.pro_bar(
                    ts_code=ts_code,
                    freq=freq,
                    start_date=start.replace("-", "") if start else None,
                    end_date=end.replace("-", "") if end else None,
                    asset="FD",
                )
            return df
        except Exception:
            return None

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化为统一DataFrame格式: open/high/low/close/volume/factor + timestamp"""
        result = pd.DataFrame()

        # 直接映射: 同名列
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                result[col] = df[col]

        # volume: Tushare用 'vol'
        if "vol" in df.columns:
            result["volume"] = df["vol"]
        elif "volume" in df.columns:
            result["volume"] = df["volume"]

        # factor
        result["factor"] = 1.0

        # timestamp: Tushare用 'trade_date' (YYYYMMDD格式)
        if "trade_date" in df.columns:
            result["timestamp"] = pd.to_datetime(
                df["trade_date"].astype(str), format="%Y%m%d", errors="coerce"
            )
        elif "timestamp" in df.columns:
            result["timestamp"] = pd.to_datetime(df["timestamp"])

        # 清理: 确保price列为float
        for col in ["open", "high", "low", "close", "volume"]:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors="coerce")

        result = result.dropna(subset=["open", "close"])

        # 关键: Tushare返回降序数据，必须升序排列（时间从早到晚）
        if "timestamp" in result.columns and not result.empty:
            result = result.sort_values("timestamp", ascending=True).reset_index(drop=True)

        return result

    async def health_check(self) -> bool:
        """健康检查 — 调用stock_basic验证连通性"""
        if self._pro is None:
            if self.token:
                self._init_pro()
            if self._pro is None:
                self._healthy = False
                return False

        try:
            df = self._pro.stock_basic(list_status="L", fields="ts_code", limit=1)
            self._healthy = df is not None and not df.empty
            return self._healthy
        except Exception:
            self._healthy = False
            return False
