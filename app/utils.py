import asyncio

from fastapi import WebSocket
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .models import WebSocketConnection


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, connection_id: str, db: AsyncSession):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        new_connection = WebSocketConnection(connection_id=connection_id)
        db.add(new_connection)
        await db.commit()

    async def disconnect(self, connection_id: str, db: AsyncSession):
        websocket = self.active_connections.pop(connection_id, None)
        if websocket:
            await websocket.close()
        await db.execute(
            text(
                "DELETE FROM websocket_connections WHERE connection_id = :connection_id"
            ),
            {"connection_id": connection_id},
        )
        await db.commit()

    async def broadcast(self, message: str):
        async with self.lock:
            for _, websocket in self.active_connections.items():
                await websocket.send_text(message)
