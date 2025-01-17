from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BoardCreate(BaseModel):
    title: str
    description: Optional[str]

class BoardUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]

class BoardResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
