from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from src.auth.models import User
from src.friends.models import Friendship
from sqlalchemy import or_, and_

async def send_friend_request(db: AsyncSession, current_user: User, receiver_id: UUID):
    if current_user.id == receiver_id:
        raise HTTPException(status_code=400, detail="Нельзя добавить самого себя")

    result = await db.execute(
        select(Friendship).where(
            Friendship.requester_id == current_user.id,
            Friendship.receiver_id == receiver_id
        )
    )
    if result.scalar():
        raise HTTPException(status_code=400, detail="Заявка уже существует")

    friendship = Friendship(requester_id=current_user.id, receiver_id=receiver_id)
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return friendship

async def accept_friend_request(db: AsyncSession, current_user: User, requester_id: UUID):
    result = await db.execute(
        select(Friendship).where(
            Friendship.requester_id == requester_id,
            Friendship.receiver_id == current_user.id,
            Friendship.is_accepted == False
        )
    )
    friendship = result.scalar_one_or_none()
    if not friendship:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    friendship.is_accepted = True
    await db.commit()
    await db.refresh(friendship)
    return friendship

async def get_friends(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(User).join(Friendship,
            ((Friendship.requester_id == current_user.id) & (Friendship.receiver_id == User.id) & (Friendship.is_accepted == True)) |
            ((Friendship.receiver_id == current_user.id) & (Friendship.requester_id == User.id) & (Friendship.is_accepted == True))
        )
    )
    return result.scalars().all()

async def get_incoming_requests(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(User)
        .join(Friendship, Friendship.requester_id == User.id)
        .where(
            Friendship.receiver_id == current_user.id,
            Friendship.is_accepted == False
        )
    )
    return result.scalars().all()

async def get_sent_requests(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(User)
        .join(Friendship, Friendship.receiver_id == User.id)
        .where(
            Friendship.requester_id == current_user.id,
            Friendship.is_accepted == False
        )
    )
    return result.scalars().all()

async def remove_friend_service(current_user: User, friend_id: UUID, db: AsyncSession):
    result = await db.execute(
        select(Friendship).where(
            and_(
                Friendship.is_accepted == True,
                or_(
                    and_(
                        Friendship.requester_id == current_user.id,
                        Friendship.receiver_id == friend_id,
                    ),
                    and_(
                        Friendship.requester_id == friend_id,
                        Friendship.receiver_id == current_user.id,
                    ),
                ),
            )
        )
    )

    friendship = result.scalars().first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Дружба не найдена")

    await db.delete(friendship)
    await db.commit()
    return {"message": "Пользователь удалён из друзей"}