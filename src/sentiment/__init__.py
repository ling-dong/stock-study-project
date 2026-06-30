"""文本情绪采集 — §4.4"""
from src.sentiment.collector import SentimentCollector, SECTOR_KEYWORDS, MARKET_KEYWORDS
from src.sentiment.cache import SentimentCache

__all__ = [
    "SentimentCollector", "SECTOR_KEYWORDS", "MARKET_KEYWORDS",
    "SentimentCache",
]
