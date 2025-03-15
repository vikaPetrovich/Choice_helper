from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from src.cards.models import Card
from src.cards.schemas import CardCreate, CardUpdate

'////////'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from src.cards.models import Card
from src.boards.models import Board, BoardCard
from src.cards.schemas import CardCreate


async def create_card_service(card_data: CardCreate, db: AsyncSession):
    new_card = Card(
        id=uuid4(),
        text=card_data.text,
        short_description=card_data.short_description,
        image_url=card_data.image_url
    )

    db.add(new_card)
    await db.commit()
    await db.refresh(new_card)

    return new_card  # Карточка создаётся без привязки к доске
'//////'
async def get_all_cards_service(skip: int, limit: int, db: AsyncSession):
    try:
        query = select(Card).offset(skip).limit(limit)
        result = await db.execute(query)
        cards = result.scalars().all()
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении карточек: {e}")

'''
async def create_card_service(card_data: CardCreate, db: AsyncSession):
    try:
        new_card = Card(
            text=card_data.text,
            short_description=card_data.short_description,
            image_url=card_data.image_url,  # Используем URL, полученный от загрузки
            status=card_data.status,
        )
        db.add(new_card)
        await db.commit()
        await db.refresh(new_card)
        return new_card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании карточки: {e}")

'''
async def get_card_service(card_id: UUID, db: AsyncSession):
    try:
        query = select(Card).where(Card.id == card_id)
        result = await db.execute(query)
        card = result.scalars().first()
        if not card:
            raise HTTPException(status_code=404, detail="Карточка не найдена")
        return card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении карточки: {e}")


async def update_card_service(card_id: UUID, card_data: CardUpdate, db: AsyncSession):
    try:
        query = select(Card).where(Card.id == card_id)
        result = await db.execute(query)
        card = result.scalars().first()
        if not card:
            raise HTTPException(status_code=404, detail="Карточка не найдена")

        # Обновление полей
        if card_data.text is not None:
            card.text = card_data.text
        if card_data.short_description is not None:
            card.short_description = card_data.short_description
        if card_data.image_url is not None:
            card.image_url = card_data.image_url
        if card_data.status is not None:
            card.status = card_data.status

        await db.commit()
        await db.refresh(card)
        return card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении карточки: {e}")



async def delete_card_service(card_id: UUID, db: AsyncSession):
    try:
        # Ищем карточку
        result = await db.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        if not card:
            raise HTTPException(status_code=404, detail="Карточка не найдена")

        # Удаляем карточку (каскадно удалятся и `board_cards`)
        await db.delete(card)
        await db.commit()

        return {"message": f"Карточка с ID {card_id} успешно удалена"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении карточки: {str(e)}")
