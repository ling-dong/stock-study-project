"""AKShare适配器 — 备用数据源(第三优先级) §7.2.2

使用东方财富ETF历史数据接口，免费无需token。
缺点: 接口随时可能变、频率限制不透明、历史覆盖约5年。
用途: 补缺 — 仅当Tushare数据有缺口时填充最近N天。
"""
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import asyncio
import logging
from src.data.adapters.base import DataAdapter

logger = logging.getLogger(__name__)


class AKShareAdapter(DataAdapter):
    """AKShare数据适配器 — §7.2.2

    ETF日线: akshare.fund_etf_hist_em()
    数据延迟: 3-5秒
    历史覆盖: 约5年
    """

    source_name = "akshare"

    def __init__(self):
        self._healthy = True
        self._ak = None

    def _get_ak(self):
        """懒加载akshare"""
        if self._ak is None:
            try:
                import akshare as ak
                self._ak = ak
                self._healthy = True
            except ImportError:
                self._healthy = False
                logger.warning("akshare未安装，备用数据源不可用")
        return self._ak

    async def get_bars(
        self,
        symbol: str,
        freq: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """获取ETF日线数据 — fund_etf_hist_em()

        Args:
            symbol: 如 "512480.SH" → AKShare用 "512480"
            freq: 仅支持 "day"（分钟线用其他接口）
        """
        ak = self._get_ak()
        if ak is None or freq != "day":
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

        try:
            # AKShare symbol格式: 去掉后缀
            code = symbol.split(".")[0]

            start_str = start.strftime("%Y%m%d") if start else "20230101"
            end_str = end.strftime("%Y%m%d") if end else datetime.now().strftime("%Y%m%d")

            # fund_etf_hist_em 是同步接口，用 asyncio.to_thread 包装
            df = await asyncio.to_thread(
                ak.fund_etf_hist_em,
                symbol=code,
                period="daily",
                start_date=start_str,
                end_date=end_str,
                adjust="qfq",  # 前复权
            )

            if df is None or df.empty:
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

            return self._standardize_akshare(df)

        except Exception as e:
            logger.debug(f"AKShare获取{symbol}失败: {e}")
            self._healthy = False
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "factor"])

    def _standardize_akshare(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化AKShare列名为SPAS统一格式"""
        col_map = {
            "日期": "timestamp",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        }
        result = pd.DataFrame()
        for cn_name, en_name in col_map.items():
            if cn_name in df.columns:
                if cn_name == "日期":
                    result[en_name] = pd.to_datetime(df[cn_name], errors="coerce")
                else:
                    result[en_name] = pd.to_numeric(df[cn_name], errors="coerce")

        result["factor"] = 1.0

        # 按时间升序
        if "timestamp" in result.columns and not result.empty:
            result = result.sort_values("timestamp", ascending=True).reset_index(drop=True)

        # 去重
        result = result.drop_duplicates(subset=["timestamp"], keep="last")

        return result.dropna(subset=["open", "close"])

    async def fetch_recent_only(
        self,
        symbol: str,
        days: int = 10,
    ) -> pd.DataFrame:
        """仅获取最近N天数据（用于补缺，减少API压力）"""
        end = datetime.now()
        start = end - timedelta(days=max(days, 30))  # 多取一些防止周末
        return await self.get_bars(symbol, "day", start, end)

    async def health_check(self) -> bool:
        """健康检查 — 尝试获取一只知名ETF的1天数据"""
        try:
            df = await self.fetch_recent_only("510300", days=1)
            self._healthy = df is not None and not df.empty
            return self._healthy
        except Exception:
            self._healthy = False
            return False
