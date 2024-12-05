from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Any
from app.schemas.users import UserCreate, UserLogin, ActivationCodeConfirm, TokenRefresh, UserProfile
from app.crud.users import UserCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import jwt
from passlib.hash import bcrypt
import uuid
import os

from app.core.security import SECRET_KEY, ALGORITHM



class AbstractUserService(ABC):
    @abstractmethod
    async def register(self, user: UserCreate) -> Any:
        pass

    @abstractmethod
    async def login(self, user: UserLogin) -> Any:
        pass

    @abstractmethod
    async def confirm_email(self, data: ActivationCodeConfirm) -> Any:
        pass

    @abstractmethod
    async def refresh_token(self, refresh: TokenRefresh) -> Any:
        pass

    @abstractmethod
    async def get_profile(self, user_id: int) -> UserProfile:
        pass


class UserService(AbstractUserService):
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)

    def _generate_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        payload = {
            "subject": {"id": user_id, "roles": ["user"]},
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def register(self, user: UserCreate) -> dict:
        existing_user = await self.user_crud.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        activation_code = str(uuid.uuid4())
        new_user = await self.user_crud.create_user(user, activation_code)
        return {"message": "Registration successful", "activation_code": activation_code}

    async def login(self, user: UserLogin) -> dict:
        db_user = await self.user_crud.get_user_by_username(user.username)
        if not db_user or not bcrypt.verify(user.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = self._generate_token(db_user.id, timedelta(minutes=15))
        refresh_token = self._generate_token(db_user.id, timedelta(days=7))
        await self.user_crud.save_tokens_to_db(db_user.id, access_token, refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        user = await self.user_crud.get_user_by_username(data.username)
        if not user or user.activation_code != data.activation_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid activation code")

        user.is_active = True
        await self.user_crud.db.commit()
        return {"message": "Email confirmed successfully"}

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        # Здесь вы проверяете refresh_token и выдаете новый access_token
        try:
            payload = jwt.decode(refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        new_access_token = self._generate_token(user_id, timedelta(minutes=15))
        return {"access_token": new_access_token}

    async def get_profile(self, user_id: int) -> UserProfile:
        user = await self.user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )