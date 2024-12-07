import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db

# Настройки тестовой базы данных
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределение зависимости get_db для использования тестовой базы данных
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
async def async_client():
    """
    Асинхронный клиент для тестирования FastAPI-приложения.
    """
    Base.metadata.create_all(bind=engine)  # Создаём таблицы перед тестами
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    Base.metadata.drop_all(bind=engine)  # Удаляем таблицы после тестов