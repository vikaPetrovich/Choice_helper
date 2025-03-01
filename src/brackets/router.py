from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.db import get_db
from src.brackets.services import create_bracket_service, get_bracket_service, vote_in_bracket_service
from src.brackets.schemas import BracketCreate, BracketResponse, VoteRequest

router = APIRouter()

@router.post("/", response_model=BracketResponse)
async def create_bracket(session_id: UUID, db: AsyncSession = Depends(get_db)):
    return await create_bracket_service(session_id, db)

@router.get("/{bracket_id}", response_model=BracketResponse)
async def get_bracket(bracket_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_bracket_service(bracket_id, db)

@router.post("/{bracket_id}/vote")
async def vote_in_bracket(bracket_id: UUID, vote_data: VoteRequest, db: AsyncSession = Depends(get_db)):
    return await vote_in_bracket_service(bracket_id, vote_data, db)
