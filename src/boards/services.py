from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.boards.models import Board
from src.boards.schemas import BoardCreate, BoardUpdate
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError

def get_all_boards_service(skip: int = 0, limit: int = 10, db: Session = None):
    try:
        boards = db.query(Board).offset(skip).limit(limit).all()
        return boards
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")

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

def get_board_service(board_id: UUID, db: Session = None):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")
    return board

def update_board_service(board_id: UUID, board_data: BoardUpdate, db: Session = None):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")
    if board_data.title is not None:
        board.title = board_data.title
    if board_data.description is not None:
        board.description = board_data.description
    db.commit()
    db.refresh(board)
    return board

def delete_board_service(board_id: UUID, db: Session = None):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")
    db.delete(board)
    db.commit()
    return {"id": str(board_id), "status": "удалена"}

