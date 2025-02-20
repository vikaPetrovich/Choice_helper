from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None

class BoardUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]

class BoardResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})

class BoardCardCreate(BaseModel):
    card_id: UUID