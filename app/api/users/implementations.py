from fastapi import HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from app.services.user_service import AbstractUserService
from app.services.profile_service import AbstractProfileService
from app.services.token_service import AbstractTokenService
from app.schemas.users import (
    PasswordChangeRequest,
    UserCreate,
    UserLogin,
    ActivationCodeConfirm,
    TokenRefresh,
    UserProfileResponse,
)
from app.api.users.abstract_apis import (
    AbstractRegisterAPI,
    AbstractLoginAPI,
    AbstractEmailConfirmAPI,
    AbstractTokenAPI,
    AbstractProfileAPI,
    AbstractPasswordChangeAPI,
)
from app.core.security import JWTAuth
from sqlalchemy.ext.asyncio import AsyncSession


class RegisterAPI(AbstractRegisterAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def register(self, user: UserCreate) -> dict:
        """Регистрация нового пользователя"""
        return await self.service.register(user)


class LoginAPI(AbstractLoginAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def login(self, user: UserLogin) -> dict:
        """Авторизация пользователя"""
        return await self.service.login(user)


class EmailConfirmAPI(AbstractEmailConfirmAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        """Подтверждение email"""
        return await self.service.confirm_email(data)


class TokenAPI(AbstractTokenAPI):
    def __init__(self, service: AbstractTokenService):
        self.service = service

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        """Обновление токенов"""
        return await self.service.refresh_token(refresh)


class ProfileAPI(AbstractProfileAPI):
    def __init__(self, service: AbstractProfileService, jwt_auth: JWTAuth, user_status_checker):
        self.service = service
        self.jwt_auth = jwt_auth
        self.user_status_checker = user_status_checker

    async def get_profile(self, credentials: JwtAuthorizationCredentials, db: AsyncSession) -> UserProfileResponse:
        """Получение профиля пользователя"""
        user_id = self.jwt_auth.extract_user_id(credentials)
        # Проверка активности пользователя
        await self.user_status_checker.check_user_active(user_id, db)
        return await self.service.get_profile(user_id)


class PasswordChangeAPI(AbstractPasswordChangeAPI):
    def __init__(self, service: AbstractProfileService, user_status_checker):
        self.service = service
        self.user_status_checker = user_status_checker

    async def change_password(self, user_id: int, data: PasswordChangeRequest, db: AsyncSession) -> dict:
        """Смена пароля пользователя"""
        # Проверка активности пользователя
        await self.user_status_checker.check_user_active(user_id, db)
        return await self.service.change_password(user_id=user_id, data=data)