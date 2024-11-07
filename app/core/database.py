from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL



# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Базовый класс для моделей
Base = declarative_base()

# Асинхронная функция для получения сессии
async def get_db():
    async with SessionLocal() as session:
        yield session

# Подключение к базе данных
async def connect():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Отключение от базы данных
async def disconnect():
    await engine.dispose()
