from fastapi import HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from app.services.user_service import AbstractUserService
from app.schemas.users import PasswordChangeRequest, UserCreate, UserLogin, ActivationCodeConfirm, TokenRefresh, UserProfileResponse
from app.api.users.abstract_apis import (
    AbstractRegisterAPI,
    AbstractLoginAPI,
    AbstractEmailConfirmAPI,
    AbstractTokenAPI,
    AbstractProfileAPI,
    AbstractPasswordChangeAPI,
    ActivationCodeConfirm,
    
)





class RegisterAPI(AbstractRegisterAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def register(self, user: UserCreate) -> dict:
        return await self.service.register(user)


class LoginAPI(AbstractLoginAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def login(self, user: UserLogin) -> dict:
        return await self.service.login(user)


class EmailConfirmAPI(AbstractEmailConfirmAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        return await self.service.confirm_email(data)


class TokenAPI(AbstractTokenAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        return await self.service.refresh_token(refresh)


class ProfileAPI(AbstractProfileAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def get_profile(self, user_id: int) -> UserProfileResponse:
        return await self.service.get_profile(user_id)
    
    
class PasswordChangeAPI(AbstractPasswordChangeAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> dict:
        return await self.service.change_password(user_id=user_id, data=data)
    

    
    
