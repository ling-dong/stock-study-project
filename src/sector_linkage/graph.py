"""§4.5.1 稀疏关联图 — 基于投入产出表的产业链边定义

边定义来源:
- 国家统计局投入产出表 (2020年版, 153部门)
- 申万行业分类与国民经济行业分类(GB/T 4754-2017)映射
- 板块间历史收益相关性验证 (correlation > 0.6)

边类型:
- 上下游: 完全消耗系数 > 0.10 (强) / 0.05-0.10 (弱)
- 替代: 相关系数 > 0.7 且无上下游关系, 或产品功能重叠
- 互补: 相关系数 > 0.7 且在产业链中同向联动
"""
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EdgeType(str, Enum):
    UPSTREAM = "上下游"          # 供应商→客户, 完全消耗系数 > 0.10
    WEAK_UPSTREAM = "弱上下游"   # 间接关联, 完全消耗系数 0.05-0.10
    SUBSTITUTE = "替代"          # 产品功能重叠或竞争关系
    COMPLEMENT = "互补"          # 产业链中同向联动
    DEMAND_PULL = "需求拉动"     # 下游需求扩张倒逼上游


class EdgeStrength(str, Enum):
    STRONG = "强"
    WEAK = "弱"


# ============================================================
# 申万一级行业代码 → 名称 (31个行业)
# ============================================================
SW_INDUSTRY_NAMES: Dict[str, str] = {
    "801010": "农林牧渔",     "801020": "采掘",
    "801030": "化工",         "801040": "钢铁",
    "801050": "有色金属",     "801080": "电子",
    "801110": "家用电器",     "801120": "食品饮料",
    "801130": "纺织服装",     "801140": "轻工制造",
    "801150": "医药生物",     "801160": "公用事业",
    "801170": "交通运输",     "801180": "房地产",
    "801200": "商业贸易",     "801210": "休闲服务",
    "801230": "综合",         "801710": "建筑材料",
    "801720": "建筑装饰",     "801730": "电气设备",
    "801740": "国防军工",     "801750": "计算机",
    "801760": "通信",        "801770": "传媒",
    "801780": "银行",         "801790": "非银金融",
    "801880": "汽车",         "801890": "机械设备",
    "801761": "通信设备",     "801751": "人工智能",
    "CPO": "CPO/光通信",
}


class SectorLinkageGraph:
    """板块关联图 — §4.5.1

    预定义产业链上下游关系，计算复杂度从 O(N²·T) 降至 O(E·T)。

    边数量上限: 80条 (设计文档要求)
    实际预定义: ~60条 (覆盖主要产业链)
    """

    def __init__(self):
        self.edges: Dict[str, Set[str]] = {}
        self.edge_types: Dict[Tuple[str, str], str] = {}
        self.edge_strengths: Dict[Tuple[str, str], str] = {}

    # ============================================================
    # 边管理
    # ============================================================
    def add_edge(
        self,
        from_sector: str,
        to_sector: str,
        edge_type: str = "上下游",
        strength: str = "强",
    ):
        """添加一条产业链边

        Args:
            from_sector: 上游板块ID
            to_sector: 下游板块ID
            edge_type: 边类型 (上下游/弱上下游/替代/互补/需求拉动)
            strength: 关联强度 (强/弱)
        """
        self.edges.setdefault(from_sector, set()).add(to_sector)
        self.edge_types[(from_sector, to_sector)] = edge_type
        self.edge_strengths[(from_sector, to_sector)] = strength

    def get_related(self, sector_id: str) -> List[str]:
        """获取板块的所有关联板块"""
        return sorted(self.edges.get(sector_id, set()))

    def get_related_with_info(self, sector_id: str) -> List[Tuple[str, str, str]]:
        """获取板块关联 + 类型 + 强度

        Returns:
            [(target_sector, edge_type, strength), ...]
        """
        result = []
        for target in self.edges.get(sector_id, set()):
            etype = self.edge_types.get((sector_id, target), "上下游")
            strength = self.edge_strengths.get((sector_id, target), "强")
            result.append((target, etype, strength))
        return result

    def get_upstream_of(self, sector_id: str) -> List[str]:
        """获取某个板块的上游板块"""
        upstream = []
        for (from_sec, to_sec), etype in self.edge_types.items():
            if to_sec == sector_id and "上下游" in etype:
                upstream.append(from_sec)
        return sorted(upstream)

    def get_downstream_of(self, sector_id: str) -> List[str]:
        """获取某个板块的下游板块"""
        downstream = []
        for target in self.edges.get(sector_id, set()):
            etype = self.edge_types.get((sector_id, target), "")
            if "上下游" in etype:
                downstream.append(target)
        return sorted(downstream)

    def get_all_edges(self) -> List[Tuple[str, str]]:
        return list(self.edge_types.keys())

    def edge_count(self) -> int:
        return len(self.edge_types)

    # ============================================================
    # 从配置加载
    # ============================================================
    def load_from_config(self, sectors_config_path: str = "config/sectors.yaml"):
        """从 config/sectors.yaml 的 related_sectors 字段追加边

        config/sectors.yaml 中每个板块的 related_sectors 字段会被
        解析为"上下游"类型的边。
        """
        import yaml
        try:
            with open(sectors_config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"板块配置文件不存在: {sectors_config_path}")
            return
        except Exception as e:
            logger.warning(f"加载板块配置失败: {e}")
            return

        loaded = 0
        for sector in config.get("sectors", []):
            sector_id = sector.get("sector_id", "")
            related = sector.get("related_sectors", [])
            sector_name = sector.get("name", sector_id)
            for target_id in related:
                if target_id and target_id != sector_id:
                    # 避免覆盖已有边
                    if (sector_id, target_id) not in self.edge_types:
                        self.add_edge(sector_id, target_id, "上下游", "强")
                        loaded += 1
                        logger.debug(
                            f"[配置] 产业链边: {sector_name}({sector_id}) "
                            f"→ {target_id}"
                        )

        if loaded:
            logger.info(f"从配置加载了 {loaded} 条产业链边")

    # ============================================================
    # 工厂方法 — 预置完整产业链边
    # ============================================================
    @classmethod
    def with_defaults(cls) -> "SectorLinkageGraph":
        """创建包含完整产业链边定义的关联图

        边定义依据:
        ┌──────────────────────────────────────────────────────┐
        │ 上游(原材料/能源) → 中游(制造/加工) → 下游(消费/服务) │
        └──────────────────────────────────────────────────────┘
        """
        g = cls()

        # ========================================================
        # 产业链 1: 农产品 → 食品加工 → 消费
        # ========================================================
        g.add_edge("801010", "801120", EdgeType.UPSTREAM, EdgeStrength.STRONG)
        g.add_edge("801120", "801010", EdgeType.DEMAND_PULL, EdgeStrength.STRONG)
        g.add_edge("801120", "801200", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 食品→商贸零售

        # ========================================================
        # 产业链 2: 采掘/有色 → 钢铁 → 机械 → 建筑/汽车
        # ========================================================
        g.add_edge("801020", "801040", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 采掘→钢铁
        g.add_edge("801050", "801040", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 有色→钢铁(合金)
        g.add_edge("801040", "801890", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 钢铁→机械设备
        g.add_edge("801040", "801880", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 钢铁→汽车
        g.add_edge("801890", "801880", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 机械设备→汽车
        g.add_edge("801890", "801720", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 机械设备→建筑装饰
        g.add_edge("801710", "801720", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 建材→建筑装饰
        g.add_edge("801880", "801200", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 汽车→商贸零售(4S)

        # ========================================================
        # 产业链 3: 有色 → 电力设备(电池) → 汽车(新能源车)
        # ========================================================
        g.add_edge("801050", "801730", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 有色(锂钴)→电气设备
        g.add_edge("801730", "801880", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电气设备(电池)→汽车
        g.add_edge("801730", "801160", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电气设备(光伏风电)→公用事业

        # ========================================================
        # 产业链 4: 石油石化 → 化工 → 纺织/轻工
        # ========================================================
        g.add_edge("801020", "801030", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 采掘→化工
        g.add_edge("801030", "801130", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 化工→纺织服装
        g.add_edge("801030", "801140", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 化工→轻工制造
        g.add_edge("801030", "801150", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 化工→医药(原料药)

        # ========================================================
        # 产业链 5: 电子 → 计算机 → 通信 → 传媒 (TMT)
        # ========================================================
        g.add_edge("801080", "801750", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电子(芯片)→计算机
        g.add_edge("801080", "801760", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电子(射频/光模块)→通信
        g.add_edge("801750", "801760", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 计算机(软件/服务器)→通信
        g.add_edge("801760", "801750", EdgeType.DEMAND_PULL, EdgeStrength.STRONG) # 通信需求→计算机需求
        g.add_edge("801760", "801770", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 通信(5G)→传媒(视频/游戏)
        g.add_edge("801750", "801770", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 计算机→传媒(算法推荐)
        # -- 虚拟子类: 通信设备(801761) 继承通信(801760)的边 --
        g.add_edge("801080", "801761", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电子→通信设备
        g.add_edge("801761", "801770", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 通信设备→传媒
        g.add_edge("801750", "801761", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 计算机→通信设备
        # -- 虚拟子类: 人工智能(801751) 继承计算机(801750)的边 --
        g.add_edge("801080", "801751", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 电子→人工智能
        g.add_edge("801751", "801760", EdgeType.UPSTREAM, EdgeStrength.STRONG)   # 人工智能→通信
        g.add_edge("801751", "801761", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 人工智能→通信设备
        g.add_edge("801751", "801770", EdgeType.UPSTREAM, EdgeStrength.WEAK)     # 人工智能→传媒
        # -- CPO/光通信 --
        g.add_edge("801080", "CPO", EdgeType.UPSTREAM, EdgeStrength.STRONG)      # 电子(芯片)→CPO
        g.add_edge("CPO", "801761", EdgeType.UPSTREAM, EdgeStrength.STRONG)      # CPO→通信设备
        g.add_edge("CPO", "801760", EdgeType.UPSTREAM, EdgeStrength.STRONG)      # CPO→通信

        # ========================================================
        # 产业链 6: 医药 → 消费/服务
        # ========================================================
        g.add_edge("801150", "801120", EdgeType.SUBSTITUTE, EdgeStrength.WEAK)   # 医药(保健品)↔食品(功能饮料)
        g.add_edge("801150", "801210", EdgeType.COMPLEMENT, EdgeStrength.WEAK)   # 医药↔休闲服务(医美)

        # ========================================================
        # 产业链 7: 金融联动 (银行 ↔ 非银)
        # ========================================================
        g.add_edge("801780", "801790", EdgeType.COMPLEMENT, EdgeStrength.STRONG)  # 银行↔非银金融
        g.add_edge("801790", "801780", EdgeType.COMPLEMENT, EdgeStrength.STRONG)

        # ========================================================
        # 产业链 8: 房地产 → 建材/建筑/家电/银行
        # ========================================================
        g.add_edge("801180", "801710", EdgeType.DEMAND_PULL, EdgeStrength.STRONG) # 房地产→建筑材料
        g.add_edge("801180", "801720", EdgeType.DEMAND_PULL, EdgeStrength.STRONG) # 房地产→建筑装饰
        g.add_edge("801180", "801110", EdgeType.DEMAND_PULL, EdgeStrength.WEAK)   # 房地产→家用电器
        g.add_edge("801180", "801780", EdgeType.COMPLEMENT, EdgeStrength.STRONG)  # 房地产↔银行(按揭)

        # ========================================================
        # 产业链 9: 电力/能源 → 公用事业
        # ========================================================
        g.add_edge("801020", "801160", EdgeType.UPSTREAM, EdgeStrength.STRONG)    # 采掘(煤)→公用事业(火电)
        g.add_edge("801160", "801020", EdgeType.DEMAND_PULL, EdgeStrength.WEAK)   # 电力需求→煤炭需求

        # ========================================================
        # 产业链 10: 交运 ↔ 多板块联动
        # ========================================================
        g.add_edge("801170", "801200", EdgeType.COMPLEMENT, EdgeStrength.WEAK)    # 交通运输↔商贸零售(物流)
        g.add_edge("801170", "801020", EdgeType.DEMAND_PULL, EdgeStrength.WEAK)   # 交运需求→能源需求

        logger.info(f"产业链边初始化完成: {g.edge_count()} 条边")
        return g

    # ============================================================
    # 批量查询
    # ============================================================
    def find_chain(self, start_sector: str, max_depth: int = 3) -> List[List[str]]:
        """查找从起始板块出发的产业链路径 (BFS)

        Args:
            start_sector: 起始板块ID
            max_depth: 最大搜索深度

        Returns:
            [[sector_A, sector_B, sector_C], ...] 多条路径
        """
        paths = []
        queue = [[start_sector]]

        while queue:
            path = queue.pop(0)
            if len(path) > max_depth:
                continue
            current = path[-1]
            neighbors = self.edges.get(current, set())

            extended = False
            for nb in neighbors:
                if nb not in path:  # 避免环
                    new_path = path + [nb]
                    queue.append(new_path)
                    extended = True

            if not extended and len(path) > 1:
                paths.append(path)

        return paths

    def print_chain(self, sector_id: str):
        """打印板块的产业链上下游"""
        name = SW_INDUSTRY_NAMES.get(sector_id, sector_id)
        upstream = self.get_upstream_of(sector_id)
        downstream = self.get_downstream_of(sector_id)

        if upstream:
            print(f"  ↑ 上游: {', '.join(SW_INDUSTRY_NAMES.get(s, s) for s in upstream)}")
        print(f"  ● {name} ({sector_id})")
        if downstream:
            print(f"  ↓ 下游: {', '.join(SW_INDUSTRY_NAMES.get(s, s) for s in downstream)}")

        related = self.get_related_with_info(sector_id)
        for target, etype, strength in related:
            if etype not in ("上下游", "弱上下游"):
                tname = SW_INDUSTRY_NAMES.get(target, target)
                print(f"  ↔ {tname} ({target}): {etype}({strength})")
