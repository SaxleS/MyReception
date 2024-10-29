from fastapi import APIRouter, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from teleport_webrtc.crud.users import UserCRUD
from teleport_webrtc.schemas.users import ActivationCodeConfirm, UserCreate, UserLogin, Token, TokenRefresh
from teleport_webrtc.core.database import get_db
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import random
from teleport_webrtc.mail_service import send_mail_verification  # Импортируем функцию отправки письма
from passlib.hash import bcrypt


import os
from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearer

# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретный ключ из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

# Инициализация JWT
jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)







# class UserAPI:
#     def __init__(self, db: Session):
#         self.crud = UserCRUD(db)

#     def create_user(self, user: UserCreate):
#         return self.crud.create_user(user)

#     def get_user(self, user_id: int):
#         user = self.crud.get_user(user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         return user

#     def get_users(self):
#         return self.crud.get_users()

# user_api = UserAPI










@router.post("/register", response_model=dict)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_crud = UserCRUD(db)
    
    # Проверяем, существует ли пользователь
    existing_user = await user_crud.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Генерация случайного 4-значного кода активации
    # activation_code = str(random.randint(1000, 9999))

    activation_code = '1234'

    # Создание нового пользователя с кодом активации
    new_user = await user_crud.create_user(user, activation_code=activation_code, is_active=False)
    
    # Отправка кода активации на email
    await send_mail_verification(user.email, activation_code)
    
    # Создание токенов
    access_token = jwt_bearer.create_access_token(
        subject={"id": new_user.id, "username": new_user.username},
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = jwt_bearer.create_refresh_token(
        subject={"id": new_user.id, "username": new_user.username},
        expires_delta=timedelta(days=1)
    )
    
    # Сохраняем токены в базу данных
    await user_crud.save_tokens_to_db(new_user.id, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "message": "Registration successful. Please check your email for the activation code."
    }



@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    user_crud = UserCRUD(db)
    
    # Получаем пользователя по имени
    authenticated_user = await user_crud.get_user_by_username(user.username)
    
    # Проверяем, что пользователь существует и введённый пароль соответствует хэшированному паролю
    if not authenticated_user or not bcrypt.verify(user.password, authenticated_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создание токенов
    access_token = jwt_bearer.create_access_token(
        subject={"id": authenticated_user.id, "username": authenticated_user.username},
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = jwt_bearer.create_refresh_token(
        subject={"id": authenticated_user.id, "username": authenticated_user.username},
        expires_delta=timedelta(days=1)
    )

    # Сохраняем токены в базу данных
    await user_crud.save_tokens_to_db(authenticated_user.id, access_token, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}




@router.post("/confirm-email")
async def confirm_email(data: ActivationCodeConfirm, db: AsyncSession = Depends(get_db)):
    user_crud = UserCRUD(db)
    user = await user_crud.get_user_by_username(data.username)  # await для асинхронного вызова
    
    if not user or user.activation_code != data.activation_code:
        raise HTTPException(status_code=400, detail="Invalid activation code")
    
    # Активация аккаунта
    user.is_active = True
    user.activation_code = None  # Удаляем код активации после подтверждения
    await db.commit()  # await для асинхронного коммита
    
    return {"message": "Email confirmed successfully!"}





@router.post("/refresh", response_model=Token)
async def refresh_token(refresh: TokenRefresh, db: AsyncSession = Depends(get_db)):
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    try:
        # Логирование входящего refresh токена
        print("Received refresh token:", refresh.refresh_token)
        
        # Декодируем токен вручную с использованием библиотеки jwt
        payload = jwt.decode(refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])        
        # Логирование ключа для кодирования/декодирования
        print("SECRET_KEY used for decoding:", SECRET_KEY)
        
        # Логирование декодированного payload
        print("Decoded payload:", payload)
        
        # Извлекаем информацию о пользователе из поля "subject", а не "sub"
        current_user = payload.get("subject")
        print("Current user:", current_user)
        
        if current_user is None:
            print("User not found in token")
            raise HTTPException(status_code=401, detail="Invalid token: subject not found")
        
        # Создаем новый access_token
        access_token = jwt_bearer.create_access_token(
            subject=current_user,  # Используем извлеченного пользователя
            expires_delta=timedelta(minutes=30)
        )
        
        # Логирование создания нового access_token
        print("Created new access token:", access_token)
        
        # Сохраняем токены в базе данных
        user_crud = UserCRUD(db)
        print(f"Saving tokens for user {current_user['id']}")
        await user_crud.save_tokens_to_db(current_user['id'], access_token, refresh.refresh_token)
        print("Tokens saved successfully")
        
        # Возвращаем обновленные токены
        return {"access_token": access_token, "refresh_token": refresh.refresh_token, "token_type": "bearer"}
    
    except jwt.ExpiredSignatureError:
        # Логирование ошибки истечения срока действия токена
        print("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError as e:
        # Логирование ошибки недействительного токена
        print(f"Invalid token error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")





@router.get("/protected")
async def protected_route(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)):
    # Извлекаем данные из токена
    user_info = credentials.subject
    return {"message": f"Hello {user_info['username']}!"}
