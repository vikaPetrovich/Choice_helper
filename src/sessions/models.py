

from src.db import Base
from uuid import uuid4
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.sql import func
from src.swipes.models import Swipe

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    board_id = Column(UUID(as_uuid=True), ForeignKey('boards.id'), nullable=False)
    type = Column(String(50), nullable=False)  # Теперь строка вместо Enum
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    swipes = relationship("Swipe", back_populates="session", cascade="all, delete-orphan")

    # Если связь с доской используется:
    board = relationship("Board", back_populates="sessions")
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")

class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    session = relationship("Session", back_populates="participants")
    user = relationship("User")