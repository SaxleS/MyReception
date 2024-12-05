import os
from fastapi import Header, HTTPException, status
from fastapi_jwt import JwtAccessBearer

# Получение секретного ключа и API-ключа из переменных окружения
SECRET_KEY = os.getenv("SECRET_KEY", "")
API_KEY = os.getenv("API_KEY", "")
ALGORITHM = "HS256"


# Настройка JWT Bearer
jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)

# Функция для проверки API-ключа
async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )