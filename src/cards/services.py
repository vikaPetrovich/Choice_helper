def get_all_cards_service():
    print("Получение списка всех карт...")
    return ["карточка_1", "карточка_2"]

def create_card_service():
    print("Создание новой карты...")
    return {"id": "1", "text": "Новая карта"}

def get_card_service(card_id: str):
    print(f"Получение информации о карте с ID: {card_id}")
    return {"id": card_id, "text": f"Карточка {card_id}"}

def update_card_service(card_id: str):
    print(f"Обновление карты с ID: {card_id}")
    return {"id": card_id, "text": f"Обновленная карточка {card_id}"}

def delete_card_service(card_id: str):
    print(f"Удаление карты с ID: {card_id}")
    return {"id": card_id, "status": "удалена"}
