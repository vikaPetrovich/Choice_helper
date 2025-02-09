from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from src.sessions.models import Session
from src.sessions.schemas import SessionCreate
from uuid import UUID

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
