import json
import random
from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, async_session
from .models import ChatMessage
from .utils import ConnectionManager


class MessageCreate(BaseModel):
    username: str
    message: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        pass


app = FastAPI(title="postgres-chat", lifespan=lifespan)


async def get_db():
    async with async_session() as session:
        yield session


@app.post("/messages/")
async def create_message(
    message_data: MessageCreate, db: AsyncSession = Depends(get_db)
):
    # Save message to database
    new_message = ChatMessage(
        username=message_data.username, message=message_data.message
    )
    db.add(new_message)
    await db.commit()

    # Execute NOTIFY outside of transaction
    async with async_session() as new_db_session:
        message_json = json.dumps(
            {"username": message_data.username, "message": message_data.message}
        )
        await new_db_session.execute(text(f"NOTIFY new_message, '{message_json}'"))
        await new_db_session.commit()

    return new_message


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    # 形容詞と一般名詞のリスト
    adjectives = [
        "quick",
        "lazy",
        "sleepy",
        "noisy",
        "hungry",
        "brave",
        "calm",
        "eager",
        "fancy",
        "glamorous",
        "happy",
        "sad",
        "angry",
        "bright",
        "dark",
        "shiny",
        "dull",
        "smooth",
        "rough",
        "gentle",
    ]
    nouns = [
        "fox",
        "dog",
        "cat",
        "mouse",
        "bear",
        "lion",
        "tiger",
        "elephant",
        "giraffe",
        "zebra",
        "wolf",
        "rabbit",
        "deer",
        "horse",
        "monkey",
        "panda",
        "koala",
        "kangaroo",
        "leopard",
        "cheetah",
    ]

    # ランダムな形容詞と一般名詞を選択
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)

    # 000から999までのランダムな数字を生成
    number = random.randint(0, 999)

    # 形容詞_一般名詞_数字の形式に変換
    connection_id = f"{adjective}_{noun}_{number:03}"

    cm = ConnectionManager()

    await cm.connect(websocket, connection_id, db)

    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )

    async def listener(connection, pid, channel, payload):
        await cm.broadcast(payload)

    await conn.add_listener("new_message", listener)

    try:
        while True:
            message = await websocket.receive_text()
            # Save message to database
            new_message = ChatMessage(username="user", message=message)
            db.add(new_message)
            await db.commit()

            # Execute NOTIFY outside of transaction
            async with async_session() as new_db_session:
                message_json = json.dumps(
                    {"message": message, "connection_id": connection_id}
                )
                await new_db_session.execute(
                    text(f"NOTIFY new_message, '{message_json}'")
                )
                await new_db_session.commit()
    except WebSocketDisconnect:
        await cm.disconnect(connection_id, db)
        await conn.remove_listener("new_message", listener)
        await conn.execute("UNLISTEN new_message")
        await conn.close()


async def get_websocket_by_connection_id(connection_id: str, db: AsyncSession):
    result = await db.execute(
        text(
            "SELECT * FROM websocket_connections WHERE connection_id = :connection_id"
        ),
        {"connection_id": connection_id},
    )
    connection = result.fetchone()
    if connection:
        return connection.websocket
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, server_header=False)
