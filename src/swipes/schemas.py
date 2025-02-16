from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class SwipeCreate(BaseModel):
    session_id: UUID
    card_id: UUID
    user_id: UUID | None
    liked: bool

class SwipeResponse(SwipeCreate):
    id: UUID
    created_at: datetime
