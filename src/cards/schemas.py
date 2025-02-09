from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class CardCreate(BaseModel):
    text: str
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = "active"

class CardStatus(str, Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"

class CardUpdate(BaseModel):
    text: Optional[str]
    short_description: Optional[str]
    image_url: Optional[str]
    status: Optional[CardStatus]
class CardResponse(BaseModel):
    id: UUID
    text: str
    short_description: Optional[str]
    image_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
