from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# Базовый класс с общей конфигурацией
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


# Модель для создания пользователя
class UserCreate(BaseSchema):
    username: str
    email: EmailStr
    password: str
    phone_number: str = Field(..., pattern=r'^\+?\d{10,15}$')  # Номер телефона в формате E.164


# Модель для отображения пользователя (ответ API)
class UserOut(BaseSchema):
    id: int
    username: str
    email: EmailStr
    is_active: bool


# Модель для токенов
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Модель для обновления токена
class TokenRefresh(BaseSchema):
    refresh_token: str


# Модель для логина пользователя
class UserLogin(BaseSchema):
    username: str
    password: str
    device_model: str
    os_version: str
    ip_address: str
    device_time: datetime
    latitude: float  # Широта
    longitude: float  # Долгота


# Модель для подтверждения активационного кода
class ActivationCodeConfirm(BaseSchema):
    username: str
    activation_code: str


# Модель профиля пользователя
class UserProfile(BaseSchema):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r'^\+?\d{10,15}$')  # Валидация номера телефона
    is_active: bool


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r'^\+?\d{10,15}$')
    is_active: bool

    class Config:
        orm_mode = True


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


