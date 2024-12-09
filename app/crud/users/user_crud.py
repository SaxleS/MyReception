from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from passlib.hash import bcrypt
from app.models.users import User
from app.schemas.users import UserCreate
from .abstract_cruds import AbstractUserCRUD
from app.models.users import Token
from app.logs.logger import Logger  # Импортируем логгер

logger = Logger.setup_logger()  # Инициализация логгера


class UserCRUD(AbstractUserCRUD):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        logger.info(f"Поиск пользователя с username: {username}")
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info(f"Пользователь с username: {username} найден")
        else:
            logger.warning(f"Пользователь с username: {username} не найден")
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        logger.info(f"Поиск пользователя с ID: {user_id}")
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info(f"Пользователь с ID: {user_id} найден")
        else:
            logger.warning(f"Пользователь с ID: {user_id} не найден")
        return user

    async def create_user(self, user: UserCreate, activation_code: str, is_active: bool = False) -> User:
        logger.info(f"Создание нового пользователя с username: {user.username}")
        hashed_password = bcrypt.hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            hashed_password=hashed_password,
            activation_code=activation_code,
            is_active=is_active
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        logger.info(f"Пользователь с username: {user.username} успешно создан")
        return db_user
    
    async def update_user(self, user: User) -> None:
        logger.info(f"Обновление данных пользователя с ID: {user.id}")
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Данные пользователя с ID: {user.id} успешно обновлены")

    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str) -> Token:
        logger.info(f"Сохранение токенов для пользователя с ID: {user_id}")
        stmt = select(Token).filter_by(user_id=user_id)
        result = await self.db.execute(stmt)
        token_record = result.scalars().first()

        if token_record:
            logger.info(f"Обновление токенов для пользователя с ID: {user_id}")
            token_record.access_token = access_token
            token_record.refresh_token = refresh_token
        else:
            logger.info(f"Создание новых токенов для пользователя с ID: {user_id}")
            token_record = Token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            self.db.add(token_record)

        await self.db.commit()
        await self.db.refresh(token_record)
        logger.info(f"Токены для пользователя с ID: {user_id} успешно сохранены")
        return token_record

    async def get_user_by_email(self, email: str) -> Optional[User]:
        logger.info(f"Поиск пользователя с email: {email}")
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info(f"Пользователь с email: {email} найден")
        else:
            logger.warning(f"Пользователь с email: {email} не найден")
        return user