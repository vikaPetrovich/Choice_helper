from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.auth.models import User
from src.auth.services import get_current_user
from src.db import get_db
from src.friends.schemas import FriendRequest, FriendResponse
from src.friends.services import (
    get_friends,
    send_friend_request,
    accept_friend_request,
    get_incoming_requests,
    get_sent_requests,
    remove_friend_service
)

router = APIRouter()

@router.post("/request/{receiver_id}", response_model=dict)
async def request_friend(
    receiver_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await send_friend_request(db, current_user, receiver_id)
    return {"message": "Заявка отправлена"}

@router.post("/accept/{requester_id}", response_model=dict)
async def accept_friend(
    requester_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await accept_friend_request(db, current_user, requester_id)
    return {"message": "Заявка принята"}

@router.get("/", response_model=List[FriendResponse])
async def list_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friends = await get_friends(db, current_user)
    return friends

@router.get("/requests/incoming", response_model=List[FriendResponse])
async def incoming_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_incoming_requests(db, current_user)

@router.get("/requests/sent", response_model=List[FriendResponse])
async def sent_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_sent_requests(db, current_user)

@router.delete("/remove/{friend_id}")
async def remove_friend(
    friend_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await remove_friend_service(current_user, friend_id, db)