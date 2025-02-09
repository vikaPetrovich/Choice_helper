from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.sessions.schemas import SessionCreate, SessionResponse
from src.sessions.services import (
    create_session_service,
    get_sessions_service,
    get_session_service,
    delete_session_service,
)

from uuid import UUID


router = APIRouter(tags=["Sessions"])

@router.post("/", response_model=SessionResponse)
async def create_session(session: SessionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_session_service(session, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании сессии: {str(e)}")

@router.get("/", response_model=list[SessionResponse])
async def get_sessions(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_sessions_service(skip=skip, limit=limit, db=db)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_session_service(session_id, db)

@router.delete("/{session_id}")
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """ Удаление сессии по ID """
    return await delete_session_service(session_id, db)