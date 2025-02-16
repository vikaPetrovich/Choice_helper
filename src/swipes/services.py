from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from src.swipes.models import Swipe
from src.swipes.schemas import SwipeCreate
from uuid import UUID

async def create_swipe_service(swipe_data: SwipeCreate, db: AsyncSession):
    new_swipe = Swipe(
        session_id=swipe_data.session_id,
        card_id=swipe_data.card_id,
        user_id=swipe_data.user_id,
        liked=swipe_data.liked,
    )
    db.add(new_swipe)
    await db.commit()
    await db.refresh(new_swipe)
    return new_swipe

async def get_swipes_by_session_service(session_id: UUID, db: AsyncSession):
    query = select(Swipe).where(Swipe.session_id == session_id)
    result = await db.execute(query)
    return result.scalars().all()
