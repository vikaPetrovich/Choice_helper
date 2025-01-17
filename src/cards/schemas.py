from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class CardCreate(BaseModel):
    text: str
    short_description: Optional[str]
    image_url: Optional[str]
    status: str


class CardUpdate(BaseModel):
    text: Optional[str]
    short_description: Optional[str]
    image_url: Optional[str]
    status: Optional[str]


class CardResponse(BaseModel):
    id: UUID
    text: str
    short_description: Optional[str]
    image_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
