from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from src.sessions.models import Session
from src.sessions.schemas import SessionCreate
from uuid import UUID
from src.sessions.models import SessionParticipant
from sqlalchemy.future import select
from sqlalchemy import func, select
from src.swipes.models import Swipe


async def create_session_service(session_data: SessionCreate, db: AsyncSession):
    try:
        new_session = Session(
            board_id=session_data.board_id,
            type=session_data.type  # Обычная строка, без Enum
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
    # 1. Получить всех участников сессии
    participants_result = await db.execute(
        select(SessionParticipant.user_id).where(SessionParticipant.session_id == session_id)
    )
    participant_ids = [row[0] for row in participants_result.fetchall()]
    total_participants = len(participant_ids)

    if total_participants == 0:
        return []

    # 2. Получить все свайпы сессии, сгруппировать по card_id
    swipes_result = await db.execute(
        select(Swipe.card_id, func.count(Swipe.id).label("likes"))
        .where(Swipe.session_id == session_id, Swipe.liked == True)
        .group_by(Swipe.card_id)
    )

    # 3. Отбираем карточки, где лайков >= 50% участников (или 100% по желанию)
    accepted_cards = []
    for card_id, like_count in swipes_result:
        if like_count == total_participants:  # 👈 здесь можно изменить на == total_participants
            accepted_cards.append({"card_id": card_id, "likes": like_count, "total": total_participants})

    return accepted_cards

async def get_sessions_by_board_service(board_id: UUID, db: AsyncSession):
    try:
        query = select(Session).where(Session.board_id == board_id)
        result = await db.execute(query)
        sessions = result.scalars().all()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении сессий: {e}")