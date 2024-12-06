from abc import ABC, abstractmethod
from typing import Optional
from app.models.users import User, Token
from app.schemas.users import UserCreate


class AbstractUserCRUD(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user: UserCreate, activation_code: str, is_active: bool = False) -> User:
        raise NotImplementedError


    @abstractmethod
    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str) -> Token:
        raise NotImplementedError

class AbstractTokenCRUD(ABC):
    @abstractmethod
    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str) -> Token:
        raise NotImplementedError