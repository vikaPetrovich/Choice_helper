from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy import func, update
from uuid import UUID
import uuid

from src.sessions.models import Session, SessionParticipant
from src.sessions.schemas import SessionCreate
from src.swipes.models import Swipe
from src.boards.models import Board
from src.auth.models import User


async def create_session_service(session_data: SessionCreate, db: AsyncSession):
    try:
        new_session = Session(
            board_id=session_data.board_id,
            type=session_data.type
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании сессии: {str(e)}")


async def get_sessions_service(skip: int, limit: int, db: AsyncSession):
    try:
        query = select(Session).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сессий: {str(e)}")


async def get_session_service(session_id: UUID, db: AsyncSession):
    try:
        query = select(Session).filter_by(id=session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        return session
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сессии: {str(e)}")


async def get_session_with_completion_flag(session_id: UUID, user_id: UUID, db: AsyncSession):
    try:
        query = select(Session).filter_by(id=session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")

        # Проверка флага завершения
        part_query = select(SessionParticipant).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user_id
        )
        result = await db.execute(part_query)
        participant = result.scalar_one_or_none()
        is_completed = participant.is_completed if participant else False

        return {
            "id": session.id,
            "board_id": session.board_id,
            "type": session.type,
            "created_at": session.created_at,
            "is_completed": is_completed
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сессии: {str(e)}")


async def delete_session_service(session_id: UUID, db: AsyncSession):
    try:
        query = select(Session).where(Session.id == session_id)
        result = await db.execute(query)
        session = result.scalars().first()

        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")

        await db.delete(session)
        await db.commit()
        return {"message": f"Сессия с ID {session_id} успешно удалена"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении сессии: {str(e)}")


async def add_participants_to_session(session_id: UUID, user_ids: list[UUID], db: AsyncSession):
    for user_id in user_ids:
        participant = SessionParticipant(session_id=session_id, user_id=user_id)
        db.add(participant)
    await db.commit()


async def get_session_results(session_id: UUID, db: AsyncSession):
    participants_result = await db.execute(
        select(SessionParticipant.user_id).where(SessionParticipant.session_id == session_id)
    )
    participant_ids = [row[0] for row in participants_result.fetchall()]
    total_participants = len(participant_ids)

    if total_participants == 0:
        return []

    swipes_result = await db.execute(
        select(Swipe.card_id, func.count(Swipe.id).label("likes"))
        .where(Swipe.session_id == session_id, Swipe.liked == True)
        .group_by(Swipe.card_id)
    )

    accepted_cards = []
    for card_id, like_count in swipes_result:
        if like_count == total_participants:
            accepted_cards.append({"card_id": card_id, "likes": like_count, "total": total_participants})

    return accepted_cards


async def get_sessions_by_board_service(board_id: UUID, user_id: UUID, db: AsyncSession):
    try:
        query = select(Session).where(Session.board_id == board_id)
        result = await db.execute(query)
        sessions = result.scalars().all()

        session_ids = [s.id for s in sessions]

        # Получаем статусы по is_completed
        part_result = await db.execute(
            select(SessionParticipant.session_id, SessionParticipant.is_completed)
            .where(SessionParticipant.session_id.in_(session_ids))
            .where(SessionParticipant.user_id == user_id)
        )
        part_map = {row[0]: row[1] for row in part_result.fetchall()}

        # Возвращаем расширенные данные
        return [
            {
                "id": s.id,
                "board_id": s.board_id,
                "type": s.type,
                "created_at": s.created_at,
                "is_completed": part_map.get(s.id, False)
            }
            for s in sessions
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сессий: {e}")


async def create_group_session_service(board_id: UUID, user_ids: list[UUID], db: AsyncSession):
    board = await db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")

    new_session = Session(
        id=uuid.uuid4(),
        board_id=board_id,
        type="group"
    )
    db.add(new_session)
    await db.flush()

    for uid in user_ids:
        user = await db.get(User, uid)
        if not user:
            raise HTTPException(status_code=404, detail=f"Пользователь {uid} не найден")
        db.add(SessionParticipant(session_id=new_session.id, user_id=uid))

    await db.commit()
    await db.refresh(new_session)
    return new_session


async def get_user_invited_sessions(user_id: UUID, db: AsyncSession):
    stmt = (
        select(Session)
        .join(SessionParticipant)
        .where(SessionParticipant.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def mark_session_completed(user_id: UUID, session_id: UUID, db: AsyncSession):
    stmt = (
        update(SessionParticipant)
        .where(SessionParticipant.user_id == user_id, SessionParticipant.session_id == session_id)
        .values(is_completed=True)
    )
    await db.execute(stmt)
    await db.commit()

async def get_session_with_completion_flag(session_id: UUID, user_id: UUID, db: AsyncSession):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    result = await db.execute(
        select(SessionParticipant).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user_id
        )
    )
    participant = result.scalar_one_or_none()
    is_completed = participant.is_completed if participant else False

    return {
        "id": session.id,
        "board_id": session.board_id,
        "type": session.type,
        "created_at": session.created_at,
        "is_completed": is_completed  # ✅ обязательно!
    }