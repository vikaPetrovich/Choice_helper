from pydantic import BaseModel
from uuid import UUID

class FriendRequest(BaseModel):
    receiver_id: UUID

class FriendResponse(BaseModel):
    id: UUID
    username: str
    email: str

    class Config:
        from_attributes = True
