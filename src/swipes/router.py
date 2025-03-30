from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.auth.services import get_current_user
from src.db import get_db
from src.swipes.schemas import SwipeCreate, SwipeResponse
from src.swipes.services import create_swipe_service, get_swipes_by_session_service

router = APIRouter()

@router.post("/", response_model=SwipeResponse)
async def create_swipe(swipe: SwipeCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await create_swipe_service(swipe, db, user_id=user.id)

@router.get("/session/{session_id}", response_model=list[SwipeResponse])
async def get_swipes(session_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_swipes_by_session_service(session_id, db)