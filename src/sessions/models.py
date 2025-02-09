

from src.db import Base

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.sql import func

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    board_id = Column(UUID(as_uuid=True), ForeignKey('boards.id'), nullable=False)
    type = Column(String(50), nullable=False)  # Теперь строка вместо Enum
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Если связь с доской используется:
    board = relationship("Board", back_populates="sessions")

