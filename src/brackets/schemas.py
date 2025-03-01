from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Optional

class BracketCreate(BaseModel):
    session_id: UUID

class BracketResponse(BaseModel):
    id: UUID
    session_id: UUID
    structure: Dict
    results: Optional[Dict]

class VoteRequest(BaseModel):
    round_number: int
    votes: Dict[str, UUID]  # Ключ – идентификатор пары, значение – ID карточки-победителя
