from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from src.db import Base
import uuid
import datetime

class Bracket(Base):
    __tablename__ = "brackets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    results = Column(JSON, nullable=True)  # теперь всё хранится здесь
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
