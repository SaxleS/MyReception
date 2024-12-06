from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from passlib.hash import bcrypt
from app.models.users import User
from app.schemas.users import UserCreate
from .abstract_cruds import AbstractUserCRUD
from app.models.users import Token


class UserCRUD(AbstractUserCRUD):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user: UserCreate, activation_code: str, is_active: bool = False) -> User:
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
        return db_user
    
    async def update_user(self, user: User) -> None:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
    

    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str) -> Token:
        stmt = select(Token).filter_by(user_id=user_id)
        result = await self.db.execute(stmt)
        token_record = result.scalars().first()

        if token_record:
            token_record.access_token = access_token
            token_record.refresh_token = refresh_token
        else:
            token_record = Token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            self.db.add(token_record)

        await self.db.commit()
        await self.db.refresh(token_record)
        return token_record