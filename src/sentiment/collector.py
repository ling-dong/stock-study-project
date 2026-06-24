"""§4.4.1 文本情绪采集 — 四级信息源优先级"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta


class SentimentCollector:
    """文本情绪采集器 — §4.4.1

    四级优先级: 官方公告 > 主流财经 > 机构研报 > 社交媒体
    权重: 官方0.4, 财经0.3, 研报0.2, 社交0.1
    """
    def __init__(self):
        self.weights = {"official": 0.4, "media": 0.3, "research": 0.2, "social": 0.1}
        self._cache: Dict[str, dict] = {}

    async def fetch(self, sector_id: str, keywords: List[str] | None = None) -> List[dict]:
        """获取板块相关文本（生产环境接入API，当前返回模拟数据）"""
        return [
            {"source": "media", "text": f"{sector_id} 板块今日活跃", "score": 0.3, "time": datetime.now()},
            {"source": "social", "text": f"{sector_id} 市场关注度提升", "score": 0.1, "time": datetime.now()},
        ]

    def aggregate_sentiment(self, items: List[dict]) -> float:
        """加权聚合情绪评分 → [-1, +1]"""
        if not items:
            return 0.0
        total_weight = 0.0
        weighted_score = 0.0
        for item in items:
            w = self.weights.get(item.get("source", "social"), 0.1)
            score = item.get("score", 0.0)
            # 时效衰减: >24小时丢弃
            age_hours = (datetime.now() - item["time"]).total_seconds() / 3600
            if age_hours > 24:
                continue
            decay = max(0.0, 1.0 - age_hours / 24.0)
            weighted_score += w * score * decay
            total_weight += w * decay
        return weighted_score / total_weight if total_weight > 0 else 0.0
