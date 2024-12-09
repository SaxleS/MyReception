from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.users import UserProfile, PasswordChangeRequest
from app.crud.users.user_crud import UserCRUD
from passlib.hash import bcrypt

from abc import ABC, abstractmethod
from app.logs.logger import Logger  # Импорт логгера

logger = Logger.setup_logger()  # Инициализация логгера


class AbstractProfileService(ABC):
    @abstractmethod
    async def get_profile(self, user_id: int) -> UserProfile:
        pass

    @abstractmethod
    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> dict:
        pass


class ProfileService(AbstractProfileService):
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)

    async def get_profile(self, user_id: int) -> UserProfile:
        logger.info(f"Запрос профиля для пользователя с ID: {user_id}")
        user = await self.user_crud.get_user_by_id(user_id)
        if not user:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"Профиль пользователя с ID {user_id} успешно получен")
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> dict:
        logger.info(f"Запрос на изменение пароля для пользователя с ID: {user_id}")
        user = await self.user_crud.get_user_by_id(user_id)
        if not user or not bcrypt.verify(data.old_password, user.hashed_password):
            logger.warning(f"Неверный старый пароль для пользователя с ID {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )

        hashed_new_password = bcrypt.hash(data.new_password)
        user.hashed_password = hashed_new_password
        await self.user_crud.update_user(user)
        logger.info(f"Пароль пользователя с ID {user_id} успешно изменен")

        return {"message": "Password updated successfully"}