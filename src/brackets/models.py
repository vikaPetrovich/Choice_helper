# app/brackets/models.py
from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSON
from src.db import Base
import uuid
import datetime

class Bracket(Base):
    __tablename__ = "bracket"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    structure = Column(JSON, nullable=False)  # Структура турнирной сетки
    results = Column(JSON, nullable=True)     # Результаты голосования
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
