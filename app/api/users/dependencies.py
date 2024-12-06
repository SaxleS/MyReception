from fastapi import Depends



from app.services.user_service import AbstractUserService, UserService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users.implementations import (
    PasswordChangeAPI,
    RegisterAPI,
    LoginAPI,
    EmailConfirmAPI,
    TokenAPI,
    ProfileAPI,
)
from app.core.security import JWTAuth




def get_user_service(db: AsyncSession = Depends(get_db)) -> AbstractUserService:
    return UserService(db=db)



def get_register_api(service: AbstractUserService = Depends(get_user_service)) -> RegisterAPI:
    return RegisterAPI(service=service)


def get_login_api(service: AbstractUserService = Depends(get_user_service)) -> LoginAPI:
    return LoginAPI(service=service)


def get_email_confirm_api(service: AbstractUserService = Depends(get_user_service)) -> EmailConfirmAPI:
    return EmailConfirmAPI(service=service)


def get_token_api(service: AbstractUserService = Depends(get_user_service)) -> TokenAPI:
    return TokenAPI(service=service)


def get_profile_api(service: AbstractUserService = Depends(get_user_service)) -> ProfileAPI:
    return ProfileAPI(service=service)


def get_password_change_api(service: AbstractUserService = Depends(get_user_service)) -> PasswordChangeAPI:
    return PasswordChangeAPI(service=service)


def get_jwt_auth_service() -> JWTAuth:
    return JWTAuth()