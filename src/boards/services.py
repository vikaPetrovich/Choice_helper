from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.boards.models import Board
from src.boards.schemas import BoardCreate, BoardUpdate
from uuid import UUID
from sqlalchemy.future import select

async def get_all_boards_service(skip: int, limit: int, db: AsyncSession):
    try:
        # Используем select для асинхронного запроса
        query = select(Board).offset(skip).limit(limit)
        result = await db.execute(query)
        boards = result.scalars().all()
        return boards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении досок: {e}")

async def create_board_service(board_data: BoardCreate, db: Session):
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
def delete_board_service(board_id: UUID, db: Session = None):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")
    db.delete(board)
    db.commit()
    return {"id": str(board_id), "status": "удалена"}

