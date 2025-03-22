from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from sqlalchemy.orm import Session

from src.boards.services import (
    get_all_boards_service,
    create_board_service,
    get_board_service,
    update_board_service,
    delete_board_service,
    add_card_to_board_service,
    get_user_boards_service
)
from src.boards.schemas import BoardCreate, BoardUpdate, BoardResponse, BoardCardCreate
from src.cards.schemas import CardResponse
from src.db import get_db
from src.auth.services import get_current_user
from src.auth.models import User

from src.auth.schemas import Token, UserCreate, UserResponse, RefreshTokenRequest




router = APIRouter()
# current_user: UserResponse = Depends(get_current_user)
# Получить все доски авторизованного пользователя
@router.get("/", response_model=list[BoardResponse])
async def get_boards(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    if skip < 0 or limit <= 0:
        raise HTTPException(status_code=400, detail="Неверные параметры пагинации")

    return await get_user_boards_service(skip=skip, limit=limit, db=db, user=current_user)

# Создать новую доску (только для авторизованного пользователя)
@router.post("/", response_model=BoardResponse)
async def create_board(board: BoardCreate, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return await create_board_service(board_data=board, db=db, user=current_user)

@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_board_service(board_id=board_id, db=db)

@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(board_id: UUID, board: BoardUpdate, db: AsyncSession = Depends(get_db)):
    return await update_board_service(board_id=board_id, board_data=board, db=db)


@router.delete("/{board_id}")
async def delete_board(board_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_board_service(board_id=board_id, db=db)

@router.post("/{board_id}/cards/", response_model=dict)
async def add_card_to_board(board_id: UUID, card_data: BoardCardCreate, db: AsyncSession = Depends(get_db)):
    return await add_card_to_board_service(board_id=board_id, card_id=card_data.card_id, db=db)

@router.get("/{board_id}/cards", response_model=list[CardResponse])
async def get_board_cards(board_id: UUID, db: AsyncSession = Depends(get_db)):
    from src.boards.services import get_cards_by_board_service
    return await get_cards_by_board_service(board_id, db)

