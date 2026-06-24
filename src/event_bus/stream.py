"""§7.1.1 Redis Streams语义的内部事件总线"""
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Tuple


class EventStream:
    """内部事件总线 — Redis Streams API兼容

    - publish(stream, event) ≈ Redis XADD
    - subscribe(stream, group, consumer) ≈ Redis XREADGROUP
    """

    def __init__(self):
        self._streams: Dict[str, List[Tuple[str, Any]]] = defaultdict(list)
        self._offsets: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._cond = asyncio.Condition()

    async def publish(self, stream: str, event: Any) -> str:
        """发布事件 — XADD语义"""
        async with self._cond:
            eid = f"{int(datetime.now().timestamp() * 1000)}-0"
            self._streams[stream].append((eid, event))
            self._cond.notify_all()
            return eid

    async def subscribe(
        self,
        stream: str,
        group: str = "default",
        consumer: str = "default",
        block_ms: int = 5000,
    ) -> AsyncIterator[Tuple[str, Any]]:
        """订阅流 — XREADGROUP语义"""
        if group not in self._offsets[stream]:
            self._offsets[stream][group] = 0

        last_idx = self._offsets[stream][group]

        while True:
            async with self._cond:
                current_len = len(self._streams[stream])
                if current_len <= last_idx:
                    try:
                        await asyncio.wait_for(
                            self._cond.wait(), timeout=block_ms / 1000
                        )
                    except asyncio.TimeoutError:
                        continue
                    current_len = len(self._streams[stream])

                while last_idx < current_len:
                    eid, event = self._streams[stream][last_idx]
                    last_idx += 1
                    yield (eid, event)

                self._offsets[stream][group] = last_idx

    async def stream_length(self, stream: str) -> int:
        """XLEN语义"""
        async with self._cond:
            return len(self._streams[stream])

    async def reset(self):
        """清空所有流（测试用）"""
        async with self._cond:
            self._streams.clear()
            self._offsets.clear()
