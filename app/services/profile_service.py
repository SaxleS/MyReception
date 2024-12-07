from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.users import UserProfile, PasswordChangeRequest
from app.crud.users.user_crud import UserCRUD
from passlib.hash import bcrypt

from abc import ABC, abstractmethod



class AbstractProfileService(ABC):
    @abstractmethod
    async def get_profile(self, user_id: int) -> UserProfile:
        pass

    @abstractmethod
    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> dict:
        pass



class ProfileService(AbstractProfileService):
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)

    async def get_profile(self, user_id: int) -> UserProfile:
        user = await self.user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> dict:
        user = await self.user_crud.get_user_by_id(user_id)
        if not user or not bcrypt.verify(data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )

        hashed_new_password = bcrypt.hash(data.new_password)
        user.hashed_password = hashed_new_password
        await self.user_crud.update_user(user)

        return {"message": "Password updated successfully"}