import os
from fastapi import Header, HTTPException, status
from fastapi_jwt import JwtAccessBearer
from abc import ABC, abstractmethod
from fastapi import HTTPException, status, Depends
from fastapi_jwt import JwtAuthorizationCredentials


from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users.user_crud import UserCRUD



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
    






class AbstractJWTAuth(ABC):
    @abstractmethod
    def extract_user_id(self, credentials: JwtAuthorizationCredentials) -> int:
        raise NotImplementedError

    
class JWTAuth(AbstractJWTAuth):
    def extract_user_id(self, credentials: JwtAuthorizationCredentials) -> int:
        """
        Извлекает user_id из токена.
        """
        user_data = credentials.subject
        if isinstance(user_data, dict) and "id" in user_data:
            return int(user_data["id"])
        elif isinstance(user_data, str):
            try:
                return int(user_data)
            except ValueError:
                pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )





class AbstractUserStatusChecker(ABC):
    @abstractmethod
    async def check_user_active(self, user_id: int, db: AsyncSession) -> None:
        """
        Проверяет, активен ли пользователь.
        """
        raise NotImplementedError
    



class UserStatusChecker(AbstractUserStatusChecker):
    async def check_user_active(self, user_id: int, db: AsyncSession) -> None:
        """
        Проверяет, активен ли пользователь.
        """
        user_crud = UserCRUD(db)
        user = await user_crud.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )