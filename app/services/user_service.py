from datetime import timedelta
from app.services.token_service import TokenService
from app.services.profile_service import ProfileService
from app.crud.users.user_crud import UserCRUD
from app.crud.users.abstract_cruds import AbstractUserCRUD, AbstractTokenCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.users import UserCreate, UserLogin, ActivationCodeConfirm
import uuid
from passlib.hash import bcrypt

from abc import ABC, abstractmethod
from app.schemas.users import UserCreate, UserLogin, ActivationCodeConfirm
from app.notifications.notification_sender_service import EmailNotificationSender
from app.celery.celery_tasks import send_verification_email_task


class AbstractUserService(ABC):

    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)
        self.token_service = TokenService()
        self.profile_service = ProfileService(db)
        self.email_sender = EmailNotificationSender()

    @abstractmethod
    async def register(self, user: UserCreate) -> dict:
        pass

    @abstractmethod
    async def login(self, user: UserLogin) -> dict:
        pass

    @abstractmethod
    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        pass

    @abstractmethod
    async def send_confirm_email_code(self, email: str) -> dict:
        pass






class UserService(AbstractUserService):  # Наследуемся от AbstractUserService



    async def register(self, user: UserCreate) -> dict:
        existing_user = await self.user_crud.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        activation_code = str(uuid.uuid4())
        new_user = await self.user_crud.create_user(user, activation_code)
        return {"message": "Registration successful"}

    async def login(self, user: UserLogin) -> dict:
        db_user = await self.user_crud.get_user_by_username(user.username)
        if not db_user or not bcrypt.verify(user.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = await self.token_service._generate_token(db_user.id, timedelta(minutes=15))
        refresh_token = await self.token_service._generate_token(db_user.id, timedelta(days=7))
        await self.user_crud.save_tokens_to_db(db_user.id, access_token, refresh_token)
        
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def confirm_email(self, data: ActivationCodeConfirm) -> dict:
        user = await self.user_crud.get_user_by_username(data.username)
        if not user or user.activation_code != data.activation_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid activation code")

        user.is_active = True
        await self.user_crud.db.commit()
        return {"message": "Email confirmed successfully"}
    



    async def send_confirm_email_code(self, email: str) -> dict:
        user = await self.user_crud.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already verified")

        # Генерация нового кода верификации
        activation_code = str(uuid.uuid4())[:4]
        user.activation_code = activation_code
        await self.user_crud.db.commit()

        # Отправка задачи через Celery
        try:
            send_verification_email_task.delay(
                recipients=[email],
                subject="MyReception - Activation Code",
                body=f"Ваш код активации: {activation_code}",
                subtype="plain",
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending email: {str(e)}")

        return {"message": "Verification code sent"}