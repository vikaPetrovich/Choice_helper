from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import List
from src.cards.schemas import CardResponse


class SessionBase(BaseModel):
    board_id: UUID
    type: Literal["individual", "collaborative"]  # Валидация значений через Literal

class SessionCreate(SessionBase):
    pass


class SessionParticipantCreate(BaseModel):
    user_ids: List[UUID]

class GroupSessionCreateRequest(BaseModel):
    board_id: UUID
    user_ids: List[UUID]

class SessionResponse(BaseModel):
    id: UUID
    board_id: UUID
    type: str
    created_at: datetime
    is_completed: bool
    is_creator: bool
    is_archived: bool

    class Config:
        from_attributes = True


class InvitedSessionResponse(BaseModel):
    id: UUID
    board_id: UUID
    type: str
    created_at: datetime
    is_completed: bool
    is_creator: bool
    is_archived: bool
    board_title: str
    board_owner_username: str

    class Config:
        from_attributes = True



class SessionAnalyticsGroup(BaseModel):
    count: int
    cards: list[CardResponse]

    class Config:
        orm_mode = True
