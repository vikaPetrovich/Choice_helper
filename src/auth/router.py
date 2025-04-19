from fastapi import APIRouter, Depends, HTTPException, status,  Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.services import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    save_refresh_token,
    authenticate_user,
    get_user,
    create_user, get_current_user,
    search_users_service
)
from src.auth.schemas import Token, UserCreate, UserResponse, RefreshTokenRequest, LoginRequest
from src.db import get_db
from pydantic import BaseModel
from typing import List
from src.auth.models import User
from src.auth.schemas import UserListResponse, UserShort
from sqlalchemy.future import select
router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация пользователя.
    """
    existing_user = await get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    db_user = await create_user(db, user)
    return UserResponse(id=db_user.id, username=db_user.username, email=db_user.email, is_active=db_user.is_active)



@router.post("/token", response_model=Token)
async def login_for_access_token(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    user = await authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    await save_refresh_token(db, user.username, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Обновление access токена по refresh токену.
    """
    user = await verify_refresh_token( refresh_data.refresh_token, db)

    new_access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    await save_refresh_token(db, user.username, new_refresh_token)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/protected", response_model=UserResponse, tags=["protected"])
async def protected_route(current_user: UserResponse = Depends(get_current_user)):
    """
    Защищенный эндпоинт: доступ только с валидным JWT-токеном.
    Теперь в Swagger вводится только сам токен без 'Bearer '.
    """
    return current_user

@router.post("/logout", response_model=dict)
async def logout(
    current_user = Depends(get_current_user),  # Используем `get_current_user`, а не `authenticate_user`
    db: AsyncSession = Depends(get_db)
):

    """ Удаляет refresh-токен пользователя, разлогинивая его. """
    current_user.refresh_token = None
    await db.commit()
    return {"message": "Вы успешно вышли из системы"}

@router.get("/users/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.get("/search", response_model=List[UserShort])
async def search_users(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await search_users_service(q, db, current_user)