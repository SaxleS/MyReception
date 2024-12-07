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
from app.core.security import AbstractUserStatusChecker, JWTAuth, UserStatusChecker
from app.services.profile_service import AbstractProfileService
from app.services.token_service import AbstractTokenService
from app.services.profile_service import ProfileService
from app.services.token_service import TokenService





def get_jwt_auth_service() -> JWTAuth:
    return JWTAuth()

def get_user_status_checker() -> UserStatusChecker:
    return UserStatusChecker()





def get_user_service(db: AsyncSession = Depends(get_db)) -> AbstractUserService:
    return UserService(db=db)

def get_profile_service(db: AsyncSession = Depends(get_db)) -> AbstractProfileService:
    return ProfileService(db=db)


def get_token_service() -> AbstractTokenService:
    return TokenService()



def get_register_api(service: AbstractUserService = Depends(get_user_service)) -> RegisterAPI:
    return RegisterAPI(service=service)


def get_login_api(service: AbstractUserService = Depends(get_user_service)) -> LoginAPI:
    return LoginAPI(service=service)


def get_email_confirm_api(service: AbstractUserService = Depends(get_user_service)) -> EmailConfirmAPI:
    return EmailConfirmAPI(service=service)



def get_token_api(service: AbstractTokenService = Depends(get_token_service)) -> TokenAPI:
    return TokenAPI(service=service)





def get_password_change_api(
    service: AbstractProfileService = Depends(get_profile_service),
    user_status_checker: AbstractUserStatusChecker = Depends(get_user_status_checker),
) -> PasswordChangeAPI:
    return PasswordChangeAPI(service=service, user_status_checker=user_status_checker)








def get_profile_api(
    service: AbstractProfileService = Depends(get_profile_service),
    jwt_auth: JWTAuth = Depends(JWTAuth),
    user_status_checker: UserStatusChecker = Depends(get_user_status_checker),
) -> ProfileAPI:
    return ProfileAPI(service=service, jwt_auth=jwt_auth, user_status_checker=user_status_checker)