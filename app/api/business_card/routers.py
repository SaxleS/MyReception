from fastapi import APIRouter, Depends, HTTPException, status
from app.api.business_card.dependencies import get_business_card_service
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
from app.schemas.business_card import BusinessCardCreate, BusinessCardResponse
from app.services.business_card.abstract_business_card_service import AbstractBusinessCardService

def get_business_card_router() -> APIRouter:
    router = APIRouter()
    jwt_auth = JWTAuth()


    @router.post(
        "/business-card/create",
        response_model=BusinessCardResponse,
        dependencies=[Depends(verify_api_key)]
    )
    async def create_or_update_business_card(
        data: BusinessCardCreate,
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service: AbstractBusinessCardService = Depends(get_business_card_service),
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        return await service.create_or_update_card(user_id, data)

    @router.get(
        "/business-card/view",
        response_model=BusinessCardResponse,
        dependencies=[Depends(verify_api_key)]
    )
    async def get_business_card(
        credentials: JwtAuthorizationCredentials = Depends(jwt_bearer),
        service: AbstractBusinessCardService = Depends(get_business_card_service),
        jwt_auth: JWTAuth = Depends(get_jwt_auth_service),
    ):
        user_id = jwt_auth.extract_user_id(credentials)
        return await service.get_card(user_id)



    @router.get(
        "/business-card/{subdomain}",
        response_model=BusinessCardResponse
    )
    async def get_card_by_subdomain(
        subdomain: str,
        service: AbstractBusinessCardService = Depends(get_business_card_service),
    ):
        return await service.get_card_by_subdomain(subdomain)

    return router





router = get_business_card_router()