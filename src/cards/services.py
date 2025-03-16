from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
from uuid import UUID
from src.cards.models import Card
from src.cards.schemas import CardCreate, CardUpdate
import os
import time
import shutil

'////////'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from src.cards.models import Card
from src.boards.models import Board, BoardCard
from src.cards.schemas import CardCreate
UPLOAD_DIR = "uploads"

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


async def update_card_service(
        card_id: UUID,
        text: str,
        short_description: str,
        status: str,
        image: UploadFile,
        db: AsyncSession,
):
    try:
        # 🔹 Логируем входные данные
        print(f"🔍 Обновление карточки {card_id} | image: {image.filename if image else 'Нет файла'}")

        # Поиск карточки в БД
        query = select(Card).where(Card.id == card_id)
        result = await db.execute(query)
        card = result.scalars().first()

        if not card:
            raise HTTPException(status_code=404, detail="Карточка не найдена")

        # 🔹 Обновляем текстовые поля
        if text is not None:
            card.text = text
        if short_description is not None:
            card.short_description = short_description
        if status is not None:
            card.status = status

        # 🔹 Если загружено новое изображение
        if image and image.filename:
            file_extension = os.path.splitext(image.filename)[1]

            # Проверяем допустимые расширения
            allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            if file_extension.lower() not in allowed_extensions:
                raise HTTPException(status_code=400, detail="Недопустимый формат файла")

            # Генерируем уникальное имя файла
            # file_path = os.path.join(UPLOAD_DIR, f"{card_id}{file_extension}")
            timestamp = int(time.time())
            file_path = f"{UPLOAD_DIR}/{timestamp}_{image.filename}"

            # 🔹 Логируем путь сохранения
            print(f"📂 Сохранение файла: {file_path}")

            # Сохраняем файл
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)

                # Обновляем путь к файлу в БД
                card.image_url = file_path
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")

        # 🔹 Коммит изменений в БД
        await db.commit()
        await db.refresh(card)

        print(f"✅ Карточка {card_id} успешно обновлена!")
        return card

    except Exception as e:
        print(f"❌ Ошибка при обновлении карточки: {e}")
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
