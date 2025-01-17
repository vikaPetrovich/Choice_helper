from fastapi import APIRouter
from src.cards.services import (
    get_all_cards_service,
    create_card_service,
    get_card_service,
    update_card_service,
    delete_card_service,
)

router = APIRouter()

@router.get("/")
def get_cards():
    data = get_all_cards_service()
    return {"message": "Список всех карт получен", "data": data}

@router.post("/")
def create_card():
    data = create_card_service()
    return {"message": "Карта создана", "data": data}

@router.get("/{card_id}")
def get_card(card_id: str):
    data = get_card_service(card_id)
    return {"message": f"Информация о карте {card_id} получена", "data": data}

@router.put("/{card_id}")
def update_card(card_id: str):
    data = update_card_service(card_id)
    return {"message": f"Карта {card_id} обновлена", "data": data}

@router.delete("/{card_id}")
def delete_card(card_id: str):
    data = delete_card_service(card_id)
    return {"message": f"Карта {card_id} удалена", "data": data}
