from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Optional

class BracketCreate(BaseModel):
    session_id: UUID

class BracketResponse(BaseModel):
    id: UUID
    session_id: UUID
    results: Optional[Dict]

class VoteRequest(BaseModel):
    round_number: int
    winner_id: UUID

class NextPairResponse(BaseModel):
    round_number: Optional[int]
    participant_1: Optional[UUID]
    participant_2: Optional[UUID]
    finished: bool