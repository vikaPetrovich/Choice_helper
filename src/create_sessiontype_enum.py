import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text  # Импортируем text для выполнения строковых запросов
from config import settings  # Убедитесь, что settings импортируется корректно

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

async def create_enum():
    async with engine.begin() as conn:
        # Проверяем, существует ли тип sessiontype, и создаем его при необходимости
        query = text("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sessiontype') THEN
                CREATE TYPE sessiontype AS ENUM ('individual', 'collaborative');
            END IF;
        END $$;
        """)
        await conn.execute(query)

async def main():
    await create_enum()

if __name__ == "__main__":
    asyncio.run(main())
