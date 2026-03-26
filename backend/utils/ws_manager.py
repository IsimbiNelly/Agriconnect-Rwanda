"""WebSocket connection manager — maps user_id → open sockets."""
import asyncio
from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)

    async def send(self, user_id: int, data: dict) -> None:
        dead = []
        for ws in list(self._connections.get(user_id, [])):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def broadcast(self, user_ids: List[int], data: dict) -> None:
        await asyncio.gather(*(self.send(uid, data) for uid in user_ids))


# Singleton used across the whole app
ws_manager = ConnectionManager()
