# app/sessions/models.py
from sqlalchemy import Column, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db import Base
import uuid
import datetime

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    type = Column(Enum("individual", "collaborative", name="session_type"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    # Relationship to swipes
    swipes = relationship("Swipe", back_populates="session")
