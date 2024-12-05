from fastapi import APIRouter, Depends, HTTPException, Header, status
from app.services.dependencies import get_user_service
from app.services.user_service import AbstractUserService, UserService
from app.schemas.users import UserCreate, UserLogin, ActivationCodeConfirm, TokenRefresh, UserProfileResponse
from app.core.database import get_db
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import os

from app.core.security import jwt_bearer, verify_api_key


class AbstractUserAPI:
    async def register(self, user: UserCreate) -> dict:
        raise NotImplementedError

    async def login(self, user: UserLogin) -> dict:
        raise NotImplementedError

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        raise NotImplementedError

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        raise NotImplementedError

    async def get_profile(self, credentials: JwtAuthorizationCredentials) -> UserProfileResponse:
        raise NotImplementedError


class UserAPI(AbstractUserAPI):
    def __init__(self, service: AbstractUserService):
        self.service = service

    async def register(self, user: UserCreate) -> dict:
        return await self.service.register(user)

    async def login(self, user: UserLogin) -> dict:
        return await self.service.login(user)

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        return await self.service.confirm_email(data)

    async def refresh_token(self, refresh: TokenRefresh) -> dict:
        return await self.service.refresh_token(refresh)

    async def get_profile(
        self,
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
    ) -> UserProfileResponse:
        user_id = int(credentials.subject)  # Получаем user_id из subject
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Используем сервис для получения профиля пользователя
        user = await self.service.get_profile(user_id)

        # Возвращаем объект Pydantic
        return UserProfileResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active
        )





def get_user_router() -> APIRouter:
    router = APIRouter()

    # Используем Depends для разрешения зависимостей
    user_api = UserAPI(service=Depends(get_user_service))

    # Регистрация маршрутов
    @router.post(
        "/register",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def register(user: UserCreate, service: AbstractUserService = Depends(get_user_service)):
        return await service.register(user)

    @router.post(
        "/login",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def login(user: UserLogin, service: AbstractUserService = Depends(get_user_service)):
        return await service.login(user)

    @router.post(
        "/confirm-email",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def confirm_email(data: ActivationCodeConfirm, service: AbstractUserService = Depends(get_user_service)):
        return await service.confirm_email(data)

    @router.post(
        "/refresh",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def refresh_token(refresh: TokenRefresh, service: AbstractUserService = Depends(get_user_service)):
        return await service.refresh_token(refresh)

    @router.get(
        "/profile",
        response_model=UserProfileResponse,
        dependencies=[Depends(verify_api_key)]
    )
    async def get_profile(
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service: AbstractUserService = Depends(get_user_service)
    ):
        return await service.get_profile(credentials.subject["id"])

    return router


router = get_user_router()