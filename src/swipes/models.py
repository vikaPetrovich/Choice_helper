# app/swipes/models.py
from sqlalchemy import Column, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db import Base
import uuid
import datetime

class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates="swipes")  # <-- вот тут связь
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # NULL для индивидуальных сессий
    liked = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="swipes")
