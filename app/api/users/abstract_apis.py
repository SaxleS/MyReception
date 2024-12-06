from abc import ABC, abstractmethod
from app.schemas.users import PasswordChangeRequest, UserCreate, UserLogin, ActivationCodeConfirm, TokenRefresh, UserProfileResponse


class AbstractRegisterAPI(ABC):
    @abstractmethod
    async def register(self, user: UserCreate) -> dict:
        raise NotImplementedError


class AbstractLoginAPI(ABC):
    @abstractmethod
    async def login(self, user: UserLogin) -> dict:
        raise NotImplementedError


class AbstractEmailConfirmAPI(ABC):
    @abstractmethod
    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        raise NotImplementedError


class AbstractTokenAPI(ABC):
    @abstractmethod
    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        raise NotImplementedError


class AbstractProfileAPI(ABC):
    @abstractmethod
    async def get_profile(self, user_id: int) -> UserProfileResponse:
        raise NotImplementedError
    

class AbstractPasswordChangeAPI(ABC):
    @abstractmethod
    async def change_password(self, data: PasswordChangeRequest) -> dict:
        raise NotImplementedError