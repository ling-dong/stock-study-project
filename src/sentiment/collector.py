"""§4.4.1 文本情绪采集 — 四级信息源优先级 + 多数据源接入

数据源:
- Tushare major_news: 8大财经媒体即时新闻 (已有token, 零成本)
- AKShare: 百度/东方财富市场情绪指数 (免费, 无需token)
- SnowNLP: 本地NLP情感打分 (离线, 无API限制)
- 本地关键词匹配: 无依赖回退方案
"""
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

# ============================================================
# 板块关键词映射 — 用于新闻匹配
# ============================================================
SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "801010": ["农林牧渔", "农业", "畜牧", "养殖", "种业", "粮食", "猪肉", "鸡肉", "水产", "牧原", "温氏"],
    "801120": ["食品饮料", "白酒", "茅台", "五粮液", "乳业", "调味品", "食品加工", "啤酒", "饮料"],
    "801180": ["医药生物", "医药", "创新药", "医疗器械", "疫苗", "生物制药", "恒瑞", "迈瑞", "药明"],
    "801750": ["计算机", "软件", "信创", "人工智能", "大数据", "云计算", "海康威视", "科大讯飞"],
    "801770": ["通信", "5G", "光模块", "光通信", "卫星通信", "算力网络", "中国联通", "中兴通讯"],
    "801760": ["半导体", "芯片", "集成电路", "光刻", "晶圆", "存储芯片", "中芯国际", "北方华创"],
    "801730": ["电力", "电力设备", "新能源", "光伏", "风电", "储能", "长江电力", "宁德时代"],
    "801020": ["煤炭", "采掘", "煤", "焦煤", "动力煤", "中国神华", "陕西煤业", "中煤能源", "兖矿"],
    "801080": ["半导体材料", "电子材料", "光刻胶", "硅片", "中微公司", "北方华创", "刻蚀", "薄膜沉积"],
    "801740": ["商业航天", "航天", "卫星", "火箭", "空间站", "中国卫星", "航天电子", "低轨"],
    "801761": ["通信设备", "5G", "基站", "光通信", "光模块", "中兴通讯", "烽火", "路由器"],
    "801751": ["人工智能", "AI", "大模型", "GPU", "算力", "深度学习", "科大讯飞", "金山办公", "ChatGPT"],
    "CPO": ["CPO", "光通信", "光模块", "共封装", "硅光", "中际旭创", "天孚通信", "新易盛", "800G", "1.6T"],
}

# 通用市场关键词（不区分板块）
MARKET_KEYWORDS = ["A股", "大盘", "上证", "深证", "沪深300", "创业板", "科创板", "牛市", "熊市"]


class SentimentCollector:
    """文本情绪采集器 — §4.4.1

    四级优先级: 官方公告(0.4) > 主流财经(0.3) > 机构研报(0.2) > 社交媒体(0.1)

    数据源优先级:
    1. Tushare major_news — 8大财经媒体 (已有token)
    2. AKShare 情绪指数 — 百度/东财聚合指标 (免费)
    3. SnowNLP 本地打分 — 离线NLP (无API限制)
    4. 关键词回退 — 纯本地, 无任何依赖
    """

    # Tushare新闻源 → SPAS来源分类
    SOURCE_MAP = {
        "新华网": "official",
        "财联社": "media",
        "华尔街见闻": "media",
        "第一财经": "media",
        "凤凰财经": "media",
        "新浪财经": "media",
        "中证网": "official",
        "同花顺": "media",
        "财新网": "research",
    }

    def __init__(
        self,
        tushare_token: Optional[str] = None,
        tushare_api_url: Optional[str] = None,
    ):
        self.weights = {"official": 0.4, "media": 0.3, "research": 0.2, "social": 0.1}
        self._cache: Dict[str, dict] = {}
        self._pro = None

        # 初始化 Tushare Pro
        if tushare_token:
            self._init_tushare(tushare_token, tushare_api_url)

        # 检查 SnowNLP 可用性
        self._snownlp_available = False
        try:
            from snownlp import SnowNLP  # noqa: F401
            self._snownlp_available = True
        except ImportError:
            logger.info("SnowNLP 未安装，将使用关键词回退方案")

    # ============================================================
    # Tushare 初始化
    # ============================================================
    def _init_tushare(self, token: str, api_url: Optional[str] = None):
        """初始化Tushare Pro连接"""
        try:
            import tushare as ts
            ts.set_token(token)
            self._pro = ts.pro_api()
            if api_url:
                self._pro._DataApi__http_url = api_url
            logger.info("Tushare Pro 新闻API 初始化成功")
        except Exception as e:
            logger.warning(f"Tushare Pro 初始化失败: {e}, 将使用回退数据源")

    # ============================================================
    # 主接口 — fetch()
    # ============================================================
    async def fetch(
        self,
        sector_id: str,
        keywords: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """获取板块相关文本情绪数据

        自动选择最优数据源:
        1. Tushare major_news → 真实新闻
        2. AKShare 情绪指数 → 聚合情绪
        3. 关键词回退 → 本地生成（无外部依赖）

        Args:
            sector_id: 板块ID, 如 "801760"
            keywords: 自定义搜索关键词
            start_date: 起始日期 "YYYY-MM-DD HH:MM:SS"
            end_date: 截止日期 "YYYY-MM-DD HH:MM:SS"

        Returns:
            [{source, text, score, time}, ...]
        """
        items = []

        # Strategy 1: Tushare major_news
        if self._pro is not None:
            tushare_items = await self._fetch_tushare_news(sector_id, keywords, start_date, end_date)
            items.extend(tushare_items)

        # Strategy 2: AKShare 市场情绪指数 (不依赖新闻内容)
        akshare_items = await self._fetch_akshare_sentiment()
        items.extend(akshare_items)

        # Strategy 3: 回退 — 如果前两步都没数据，返回带标记的空结果让上游用默认值
        if not items:
            return []

        return items

    # ============================================================
    # Tushare major_news 接入
    # ============================================================
    async def _fetch_tushare_news(
        self,
        sector_id: str,
        keywords: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """从Tushare major_news获取真实财经新闻"""
        if self._pro is None:
            return []

        # 构建搜索关键词
        search_keywords = keywords or []
        if sector_id in SECTOR_KEYWORDS:
            search_keywords.extend(SECTOR_KEYWORDS[sector_id])

        # 默认时间范围: 最近24小时
        now = datetime.now()
        if start_date is None:
            start_date = (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        if end_date is None:
            end_date = now.strftime("%Y-%m-%d %H:%M:%S")

        all_items = []
        sources_to_try = ["财联社", "新浪财经", "华尔街见闻", "第一财经", "新华网"]

        for src in sources_to_try:
            try:
                df = self._pro.major_news(
                    src=src,
                    start_date=start_date,
                    end_date=end_date,
                    fields="title,content,pub_time,src",
                )
                if df is None or df.empty:
                    continue

                import pandas as pd
                for _, row in df.iterrows():
                    title = str(row.get("title", ""))
                    content = str(row.get("content", ""))
                    full_text = f"{title} {content}"

                    # 关键词匹配过滤
                    matched = any(kw in full_text for kw in search_keywords)
                    if not matched and search_keywords:
                        continue

                    # SnowNLP 情感打分
                    score = self._score_text(full_text)

                    pub_time = row.get("pub_time")
                    try:
                        if isinstance(pub_time, str):
                            pub_time = pd.to_datetime(pub_time).to_pydatetime()
                    except Exception:
                        pub_time = now

                    source_type = self.SOURCE_MAP.get(src, "media")
                    all_items.append({
                        "source": source_type,
                        "text": title[:200],  # 截断长文本
                        "score": score,
                        "time": pub_time,
                    })

            except Exception as e:
                logger.debug(f"Tushare {src} 新闻获取失败: {e}")
                continue

        logger.info(f"Tushare新闻: {len(all_items)}条匹配 '{sector_id}'")
        return all_items

    # ============================================================
    # AKShare 市场情绪指数
    # ============================================================
    async def _fetch_akshare_sentiment(self) -> List[dict]:
        """从AKShare获取市场情绪指数（免费，无需token）"""
        items = []
        now = datetime.now()

        try:
            import akshare as ak
            # 百度情绪指数
            try:
                df = ak.stock_news_sentiment_baidu()
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    score = float(latest.get("sentiment", 0)) if "sentiment" in df.columns else 0.0
                    # 映射到 [-1, +1]
                    score = max(-1.0, min(1.0, score / 50.0))
                    items.append({
                        "source": "social",
                        "text": f"百度市场情绪指数: {score:.2f}",
                        "score": score,
                        "time": now,
                    })
            except Exception:
                pass

            # 东方财富情绪指数
            try:
                df = ak.stock_emotion_dc_index()
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    score = float(latest.get("sentiment", 0)) if "sentiment" in df.columns else 0.0
                    score = max(-1.0, min(1.0, score / 50.0))
                    items.append({
                        "source": "social",
                        "text": f"东方财富情绪指数: {score:.2f}",
                        "score": score,
                        "time": now,
                    })
            except Exception:
                pass

        except ImportError:
            logger.debug("AKShare 未安装，跳过市场情绪指数")
        except Exception as e:
            logger.debug(f"AKShare 情绪指数获取失败: {e}")

        return items

    # ============================================================
    # 情感打分引擎
    # ============================================================
    def _score_text(self, text: str) -> float:
        """对文本做情感打分 → [-1, +1]

        优先级: SnowNLP > 关键词匹配
        """
        if not text:
            return 0.0

        # 方案1: SnowNLP (已安装)
        if self._snownlp_available:
            try:
                from snownlp import SnowNLP
                s = SnowNLP(text)
                # SnowNLP.sentiments ∈ [0, 1], 0=负面 1=正面
                raw = s.sentiments
                return (raw - 0.5) * 2.0  # → [-1, +1]
            except Exception:
                pass

        # 方案2: 关键词回退
        return self._keyword_score(text)

    def _keyword_score(self, text: str) -> float:
        """基于关键词的情感打分（零依赖回退）"""
        positive_words = [
            "上涨", "涨停", "利好", "突破", "增长", "盈利", "回暖", "反弹",
            "创新高", "净流入", "超预期", "业绩增长", "政策支持", "补贴",
            "放量", "突破", "强势", "领涨", "龙头",
        ]
        negative_words = [
            "下跌", "跌停", "利空", "跌破", "亏损", "下滑", "衰退", "崩盘",
            "创新低", "净流出", "不及预期", "业绩下滑", "监管", "处罚",
            "缩量", "破位", "弱势", "领跌", "爆雷",
        ]

        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        total = pos_count + neg_count

        if total == 0:
            return 0.0

        return (pos_count - neg_count) / max(total, 5)  # 归一化

    # ============================================================
    # 情绪聚合
    # ============================================================
    def aggregate_sentiment(self, items: List[dict]) -> float:
        """加权聚合情绪评分 → [-1, +1]

        含时效衰减: >24小时丢弃
        """
        if not items:
            return 0.0
        total_weight = 0.0
        weighted_score = 0.0
        for item in items:
            w = self.weights.get(item.get("source", "social"), 0.1)
            score = item.get("score", 0.0)
            # 时效衰减: >24小时丢弃
            item_time = item.get("time", datetime.now())
            age_hours = (datetime.now() - item_time).total_seconds() / 3600
            if age_hours > 24:
                continue
            decay = max(0.0, 1.0 - age_hours / 24.0)
            weighted_score += w * score * decay
            total_weight += w * decay
        return weighted_score / total_weight if total_weight > 0 else 0.0

    # ============================================================
    # 辅助方法
    # ============================================================
    def has_tushare(self) -> bool:
        """检查Tushare是否可用"""
        return self._pro is not None

    def has_snownlp(self) -> bool:
        """检查SnowNLP是否可用"""
        return self._snownlp_available
