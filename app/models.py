from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    message = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class WebSocketConnection(Base):
    __tablename__ = "websocket_connections"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(String, unique=True, index=True)
