from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal
from datetime import datetime

class SessionBase(BaseModel):
    board_id: UUID
    type: Literal["individual", "collaborative"]  # Валидация значений через Literal

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
