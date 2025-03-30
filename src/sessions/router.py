from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.sessions.schemas import SessionCreate, SessionResponse, GroupSessionCreateRequest
from src.sessions.schemas import SessionParticipantCreate
from src.sessions.services import add_participants_to_session, get_sessions_by_board_service, \
    get_session_with_completion_flag
from src.sessions.services import (
    create_session_service,
    get_sessions_service,
    get_session_service,
    delete_session_service,
    get_session_results,
    add_participants_to_session
)
from src.auth.models import User
from src.auth.services import get_current_user
from uuid import UUID
from src.sessions.schemas import  SessionResponse
from src.sessions.services import create_group_session_service
from src.sessions.services import get_user_invited_sessions
from src.sessions.schemas import InvitedSessionResponse
from typing import List
from src.sessions.services import mark_session_completed

router = APIRouter(tags=["Sessions"])

@router.get("/", response_model=list[SessionResponse])
async def get_sessions(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_sessions_service(skip=skip, limit=limit, db=db)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_session_with_completion_flag(session_id, user.id, db)

@router.delete("/{session_id}")
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """ Удаление сессии по ID """
    return await delete_session_service(session_id, db)

@router.post("/{session_id}/participants", response_model=dict)
async def add_session_participants(
    session_id: UUID,
    data: SessionParticipantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await add_participants_to_session(session_id, data.user_ids, db)
    return {"message": "Пользователи добавлены в сессию"}

@router.get("/{session_id}/results", response_model=list[dict])
async def session_results(session_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await get_session_results(session_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-board/{board_id}", response_model=list[SessionResponse])
async def get_sessions_by_board(board_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_sessions_by_board_service(board_id, user.id, db)


@router.post("/group", response_model=SessionResponse)
async def create_group_session(
    payload: GroupSessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    session = await create_group_session_service(payload.board_id, payload.user_ids, db, creator_id=user.id)

    return {
        "id": session.id,
        "board_id": session.board_id,
        "type": session.type,
        "created_at": session.created_at,
        "is_completed": False,       # ⬅️ всегда False при создании
        "is_creator": True,          # ⬅️ текущий пользователь — инициатор
        "is_archived": False         # ⬅️ по умолчанию не архивировано
    }

@router.post("/{session_id}/complete")
async def complete_session(session_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await mark_session_completed(user.id, session_id, db)
    return {"detail": "Сессия завершена"}

@router.get("/group/invited", response_model=List[SessionResponse])
async def get_user_group_sessions(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await get_user_invited_sessions(user.id, db)
