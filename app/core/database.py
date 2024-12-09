from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL, CHAT_MONGO_URI, CHAT_DATABASE_NAME
import os


from motor.motor_asyncio import AsyncIOMotorClient





from app.logs.logger import Logger

logger = Logger.setup_logger()

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






# MongoDB

# MongoDB
# MongoDB настройки
class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.uri = CHAT_MONGO_URI
        self.database_name = CHAT_DATABASE_NAME

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.database_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

mongodb = MongoDB()

