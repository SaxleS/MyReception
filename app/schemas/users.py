from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str  # Добавляем поле для номера телефона

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    username: str
    password: str
    device_model: str
    os_version: str
    ip_address: str
    device_time: datetime
    latitude: float  # Добавляем широту
    longitude: float  # Добавляем долготу


class ActivationCodeConfirm(BaseModel):
    username: str
    activation_code: str




class UserProfile(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone_number: Optional[str] = None