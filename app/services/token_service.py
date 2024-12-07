from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from fastapi import HTTPException, status
from app.core.security import SECRET_KEY, ALGORITHM
from abc import ABC, abstractmethod
from app.schemas.users import TokenRefresh


class AbstractTokenService(ABC):
    @abstractmethod
    async def _generate_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Асинхронная генерация JWT токена"""
        pass

    @abstractmethod
    async def decode_token(self, token: str) -> int:
        """Асинхронное декодирование JWT токена"""
        pass

    @abstractmethod
    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        """Асинхронное обновление токена"""
        pass


class TokenService(AbstractTokenService):
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def _generate_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        payload = {
            "subject": {"id": user_id, "roles": ["user"]},
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            return int(user_id)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        try:
            payload = jwt.decode(refresh.refresh_token, self.secret_key, algorithms=[self.algorithm])
            subject = payload.get("subject")  # Извлекаем subject вместо sub
            if not subject or "id" not in subject:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            user_id = subject["id"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        new_access_token = await self._generate_token(user_id, timedelta(minutes=15))
        return {"access_token": new_access_token}