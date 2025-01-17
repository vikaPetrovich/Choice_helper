from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронное подключение к базе данных
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()

# Базовый класс для всех моделей
Base = declarative_base()

# Зависимость для получения сессии
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()  # Используйте await для закрытия сессии
