"""§4.5.1 稀疏关联图 — 预定义产业链边(~80条)"""
from typing import List, Dict, Set


class SectorLinkageGraph:
    """板块关联图 — §4.5.1

    预定义产业链上下游关系，计算复杂度从O(N^2·T)降至O(E·T)。
    """
    def __init__(self):
        self.edges: Dict[str, Set[str]] = {}
        self.edge_types: Dict[tuple, str] = {}

    def add_edge(self, from_sector: str, to_sector: str, edge_type: str = "上下游"):
        self.edges.setdefault(from_sector, set()).add(to_sector)
        self.edge_types[(from_sector, to_sector)] = edge_type

    def get_related(self, sector_id: str) -> List[str]:
        return list(self.edges.get(sector_id, set()))

    def get_all_edges(self) -> List[tuple]:
        return list(self.edge_types.keys())

    def edge_count(self) -> int:
        return len(self.edge_types)

    @classmethod
    def with_defaults(cls) -> "SectorLinkageGraph":
        g = cls()
        # 核心产业链
        g.add_edge("801750", "801770", "上下游")  # 计算机→通信
        g.add_edge("801180", "801120", "替代")    # 医药→食品
        g.add_edge("801120", "801010", "上下游")  # 食品→农业
        return g
