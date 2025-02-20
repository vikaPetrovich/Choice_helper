from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.boards.models import Board, BoardCard
from src.boards.schemas import BoardCreate, BoardUpdate
from uuid import UUID
from sqlalchemy.future import select
import uuid
from src.cards.models import Card

async def get_all_boards_service(skip: int, limit: int, db: AsyncSession):
    try:
        # Используем select для асинхронного запроса
        query = select(Board).offset(skip).limit(limit)
        result = await db.execute(query)
        boards = result.scalars().all()
        return boards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении досок: {e}")

async def create_board_service(board_data: BoardCreate, db: AsyncSession):
    try:
        new_board = Board(
            title=board_data.title,
            description=board_data.description,
        )
        db.add(new_board)
        await db.commit()
        await db.refresh(new_board)
        return new_board
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании доски: {e}")

async def get_board_service(board_id: UUID, db: AsyncSession):
    try:
        query = select(Board).where(Board.id == board_id)
        result = await db.execute(query)
        board = result.scalars().first()
        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")
        return board
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении доски: {e}")
async def update_board_service(board_id: UUID, board_data: BoardUpdate, db: AsyncSession):
    try:
        # Используем асинхронный запрос для поиска доски
        query = select(Board).where(Board.id == board_id)
        result = await db.execute(query)
        board = result.scalars().first()

        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")

        # Обновление полей доски
        if board_data.title is not None:
            board.title = board_data.title
        if board_data.description is not None:
            board.description = board_data.description

        await db.commit()  # Сохраняем изменения
        await db.refresh(board)  # Обновляем объект доски
        return board
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении доски: {e}")
async def delete_board_service(board_id: UUID, db: AsyncSession):
    try:
        # Асинхронный запрос для получения доски
        query = select(Board).where(Board.id == board_id)
        result = await db.execute(query)
        board = result.scalars().first()

        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")

        await db.delete(board)  # Удаление доски
        await db.commit()       # Сохранение изменений
        return {"message": f"Доска с ID {board_id} успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении доски: {e}")

async def add_card_to_board_service(board_id: UUID, card_id: UUID, db: AsyncSession):
    try:
        # Проверяем, существует ли доска
        board_query = select(Board).where(Board.id == board_id)
        result = await db.execute(board_query)
        board = result.scalars().first()
        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")

        # Проверяем, существует ли карточка
        card_query = select(BoardCard).where(BoardCard.card_id == card_id, BoardCard.board_id == board_id)
        result = await db.execute(card_query)
        existing_link = result.scalars().first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Карточка уже привязана к этой доске")

        # Добавляем связь
        board_card = BoardCard(id=uuid.uuid4(), board_id=board_id, card_id=card_id)
        db.add(board_card)
        await db.commit()
        await db.refresh(board_card)

        return {"message": "Карточка успешно привязана к доске"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при привязке карточки: {str(e)}")

async def get_cards_by_board_service(board_id: UUID, db: AsyncSession):
    try:
        query = select(BoardCard).where(BoardCard.board_id == board_id)
        result = await db.execute(query)
        board_cards = result.scalars().all()

        if not board_cards:
            return []

        card_ids = [board_card.card_id for board_card in board_cards]
        card_query = select(Card).where(Card.id.in_(card_ids))
        result = await db.execute(card_query)
        cards = result.scalars().all()
        return cards

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении карточек: {e}")

