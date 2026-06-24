"""§4.4 文本情绪缓存 — TTL=30min, 非阻塞查询"""
from typing import Optional
from datetime import datetime, timedelta


class SentimentCache:
    """情绪评分缓存 — T+5分钟延迟, TTL=30分钟"""
    def __init__(self, ttl_minutes: int = 30):
        self.ttl = timedelta(minutes=ttl_minutes)
        self._cache: dict[str, tuple[datetime, float]] = {}

    def get(self, sector_id: str) -> Optional[float]:
        """非阻塞查询，未命中返回None（下游使用中性默认值）"""
        entry = self._cache.get(sector_id)
        if entry is None:
            return None
        ts, score = entry
        if datetime.now() - ts > self.ttl:
            del self._cache[sector_id]
            return None
        return score

    def set(self, sector_id: str, score: float):
        self._cache[sector_id] = (datetime.now(), score)
