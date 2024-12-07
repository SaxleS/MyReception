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

def get_user_router() -> APIRouter:
    router = APIRouter()
    jwt_auth = JWTAuth()

    
    @router.post(
        "/register",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def register(
        user: UserCreate,
        service=Depends(get_register_api)
    ):
        return await service.register(user)

    @router.post(
        "/login",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def login(
        user: UserLogin,
        service=Depends(get_login_api)
    ):
        return await service.login(user)

    @router.post(
        "/confirm-email",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def confirm_email(
        data: ActivationCodeConfirm,
        service=Depends(get_email_confirm_api)
    ):
        return await service.confirm_email(data)

    @router.post(
        "/refresh",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def refresh_token(
        refresh: TokenRefresh,
        service=Depends(get_token_api)
    ):
        return await service.refresh_token(refresh)

    @router.get(
        "/profile",
        response_model=UserProfileResponse,
        dependencies=[Depends(verify_api_key)]
    )
    async def get_profile(
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service=Depends(get_profile_api),
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
        db: AsyncSession = Depends(get_db),  # Передаём `db` через Depends
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        return await service.get_profile(credentials, db)
    





    @router.post(
        "/change-password",
        response_model=dict,
        dependencies=[Depends(verify_api_key)]
    )
    async def change_password(
        data: PasswordChangeRequest,
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service: PasswordChangeAPI = Depends(get_password_change_api),
        db: AsyncSession = Depends(get_db),  # Добавлено
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        return await service.change_password(user_id=user_id, data=data, db=db)  # Передача db






    @router.post("/send-verification-code")
    async def send_verification_code(
        email: str,
        user_service: UserService = Depends(get_user_service)
    ):
        """
        Эндпоинт для отправки кода верификации на email.
        """
        return await user_service.send_confirm_email_code(email)




    return router





router = get_user_router()