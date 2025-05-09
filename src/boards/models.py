# app/boards/models.py

from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db import Base
import uuid
import datetime
from uuid import uuid4
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from src.db import Base
from src.auth.models import User



class Board(Base):
    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                      nullable=False)  # ✅ Должен быть UUID
    owner = relationship("User", back_populates="boards")  # Связь с пользователем

    sessions = relationship("Session", back_populates="board", cascade="all, delete-orphan")
    cards = relationship("BoardCard", back_populates="board", cascade="all, delete-orphan")

class BoardCard(Base):
    __tablename__ = "board_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)

    board = relationship("Board", back_populates="cards")
    card = relationship("Card", back_populates="boards")