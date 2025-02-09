# app/boards/models.py

from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db import Base
import uuid
import datetime
from uuid import uuid4
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from src.db import Base

class Board(Base):
    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sessions = relationship("Session", back_populates="board", cascade="all, delete-orphan")
    cards = relationship("BoardCard", back_populates="board", cascade="all, delete-orphan")


class BoardCard(Base):
    __tablename__ = "board_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)

    board = relationship("Board", back_populates="cards")
    card = relationship("Card", back_populates="boards")