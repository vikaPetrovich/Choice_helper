# app/cards/models.py
from sqlalchemy import Column, String, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db import Base
import uuid
import datetime

class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    status = Column(Enum("active", "archived", "deleted", name="card_status"), default="active")
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    boards = relationship("BoardCard", back_populates="card")


