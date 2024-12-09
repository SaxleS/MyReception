from fastapi import APIRouter, Depends, HTTPException, status
from app.api.users.implementations import PasswordChangeAPI
from app.api.users.dependencies import (
    get_jwt_auth_service,
    get_password_change_api,
    get_register_api,
    get_login_api,
    get_email_confirm_api,
    get_token_api,
    get_profile_api,
    get_user_service,
)
from app.schemas.users import PasswordChangeRequest, UserCreate, UserLogin, ActivationCodeConfirm, TokenRefresh, UserProfileResponse
from app.core.security import JWTAuth, jwt_bearer, verify_api_key
from fastapi_jwt import JwtAuthorizationCredentials
from app.core.security import JWTAuth
from sqlalchemy.ext.asyncio import AsyncSession



from app.services.user_service import UserService
from app.core.database import get_db

from app.logs.logger import Logger

logger = Logger.setup_logger()


def get_user_router() -> APIRouter:
    router = APIRouter()
    jwt_auth = JWTAuth()

    @router.post(
        "/register",
        response_model=dict,
    )
    async def register(
        user: UserCreate,
        service=Depends(get_register_api)
    ):
        logger.info(f"Регистрация нового пользователя: {user.username}")
        try:
            response = await service.register(user)
            logger.info(f"Пользователь {user.username} успешно зарегистрирован")
            return response
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя {user.username}: {e}")
            raise e

    @router.post(
        "/login",
        response_model=dict,
    )
    async def login(
        user: UserLogin,
        service=Depends(get_login_api)
    ):
        logger.info(f"Вход пользователя: {user.username}")
        try:
            response = await service.login(user)
            logger.info(f"Пользователь {user.username} успешно вошел в систему")
            return response
        except Exception as e:
            logger.error(f"Ошибка при входе пользователя {user.username}: {e}")
            raise e

    @router.post(
        "/confirm-email",
        response_model=dict,
    )
    async def confirm_email(
        data: ActivationCodeConfirm,
        service=Depends(get_email_confirm_api)
    ):
        logger.info(f"Подтверждение email с кодом: {data.activation_code}")
        try:
            response = await service.confirm_email(data)
            logger.info(f"Email подтвержден для пользователя с кодом {data.activation_code}")
            return response
        except Exception as e:
            logger.error(f"Ошибка подтверждения email с кодом {data.activation_code}: {e}")
            raise e

    @router.post(
        "/refresh",
        response_model=dict,
    )
    async def refresh_token(
        refresh: TokenRefresh,
        service=Depends(get_token_api)
    ):
        logger.info(f"Обновление токена: {refresh.refresh_token}")
        try:
            response = await service.refresh_token(refresh)
            logger.info("Токен успешно обновлен")
            return response
        except Exception as e:
            logger.error(f"Ошибка обновления токена: {e}")
            raise e

    @router.get(
        "/profile",
        response_model=UserProfileResponse,
    )
    async def get_profile(
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service=Depends(get_profile_api),
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
        db: AsyncSession = Depends(get_db),
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        logger.info(f"Получение профиля для пользователя ID: {user_id}")
        try:
            response = await service.get_profile(credentials, db)
            logger.info(f"Профиль пользователя ID: {user_id} успешно получен")
            return response
        except Exception as e:
            logger.error(f"Ошибка получения профиля пользователя ID: {user_id}: {e}")
            raise e

    @router.post(
        "/change-password",
        response_model=dict,
    )
    async def change_password(
        data: PasswordChangeRequest,
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service: PasswordChangeAPI = Depends(get_password_change_api),
        db: AsyncSession = Depends(get_db),
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        logger.info(f"Смена пароля для пользователя ID: {user_id}")
        try:
            response = await service.change_password(user_id=user_id, data=data, db=db)
            logger.info(f"Пароль пользователя ID: {user_id} успешно изменен")
            return response
        except Exception as e:
            logger.error(f"Ошибка смены пароля для пользователя ID: {user_id}: {e}")
            raise e

    @router.post("/send-verification-code")
    async def send_verification_code(
        email: str,
        user_service: UserService = Depends(get_user_service)
    ):
        logger.info(f"Отправка кода верификации на email: {email}")
        try:
            response = await user_service.send_confirm_email_code(email)
            logger.info(f"Код верификации успешно отправлен на email: {email}")
            return response
        except Exception as e:
            logger.error(f"Ошибка отправки кода верификации на email {email}: {e}")
            raise e

    return router


router = get_user_router()