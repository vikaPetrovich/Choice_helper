from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.cards.services import (
    get_all_cards_service,
    create_card_service,
    get_card_service,
    update_card_service,
    delete_card_service,
)
from src.cards.schemas import CardCreate, CardUpdate, CardResponse
from src.db import get_db

router = APIRouter()

@router.get("/", response_model=list[CardResponse])
async def get_cards(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_all_cards_service(skip=skip, limit=limit, db=db)

@router.post("/", response_model=CardResponse)
async def create_card(card: CardCreate, db: AsyncSession = Depends(get_db)):
    return await create_card_service(card_data=card, db=db)

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(card_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_card_service(card_id=card_id, db=db)

@router.put("/{card_id}", response_model=CardResponse)
async def update_card(card_id: UUID, card: CardUpdate, db: AsyncSession = Depends(get_db)):
    return await update_card_service(card_id=card_id, card_data=card, db=db)

@router.delete("/{card_id}")
async def delete_card(card_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_card_service(card_id=card_id, db=db)

