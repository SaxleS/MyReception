from sqlalchemy.orm import Session
from app.models.users import User, Token 
from app.schemas.users import UserCreate
from passlib.hash import bcrypt

from sqlalchemy.future import select
from app.schemas.users import UserCreate
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession


class UserCRUD:
    def __init__(self, db: AsyncSession):  # Используем AsyncSession
        self.db = db

    async def get_user_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user: UserCreate, activation_code: str, is_active: bool = False):
        hashed_password = bcrypt.hash(user.password)
        db_user = User(
            username=user.username, 
            email=user.email, 
            hashed_password=hashed_password,
            activation_code=activation_code,  # Устанавливаем код активации
            is_active=is_active  # Аккаунт активен или нет
        )
        self.db.add(db_user)
        await self.db.commit()  # Используем await для асинхронных методов
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, username: str, password: str):
        user = await self.get_user_by_username(username)  # Не забываем await
        if not user or not bcrypt.verify(password, user.hashed_password):
            return False
        return user
    

        # Метод для сохранения токенов в базу данных
    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str):
        # Используем select для асинхронного запроса
        result = await self.db.execute(select(Token).filter_by(user_id=user_id))
        token_record = result.scalars().first()

        if token_record:
            # Если токен уже существует, обновляем его
            token_record.access_token = access_token
            token_record.refresh_token = refresh_token
            await self.db.commit()
            await self.db.refresh(token_record)  # Обновляем запись
        else:
            # Если токена нет, создаем новую запись
            new_token = Token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            self.db.add(new_token)
            await self.db.commit()
            await self.db.refresh(new_token)  # Обновляем и возвращаем новую запись
            token_record = new_token

        return token_record