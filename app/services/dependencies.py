from app.services.user_service import AbstractUserService, UserService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

def get_user_service(db: AsyncSession = Depends(get_db)) -> AbstractUserService:
    return UserService(db=db)