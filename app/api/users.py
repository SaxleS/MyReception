from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Header, status
import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import random
from passlib.hash import bcrypt



from app.crud.users import UserCRUD
from app.models.users import User
from app.schemas.users import ActivationCodeConfirm, UserCreate, UserLogin, Token, TokenRefresh, UserProfile
from app.core.database import get_db
from app.mail_service import send_mail_verification  # Импортируем функцию отправки письма



import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретный ключ из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY")
# Читаем секретные ключи из переменных окружения
API_KEY = os.getenv("API_KEY")
router = APIRouter()

# Инициализация JWT
jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)


# Зависимость для проверки API-ключа
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )









@router.post("/register", response_model=dict, dependencies=[Depends(verify_api_key)])
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




@router.post("/login", response_model=Token, dependencies=[Depends(verify_api_key)])
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    user_crud = UserCRUD(db)
    
    # Получаем пользователя по имени
    authenticated_user = await user_crud.get_user_by_username(user.username)
    
    # Проверяем, что пользователь существует и введённый пароль соответствует хэшированному паролю
    if not authenticated_user or not bcrypt.verify(user.password, authenticated_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Обновляем информацию об устройстве и геолокации
    authenticated_user.device_model = user.device_model
    authenticated_user.os_version = user.os_version
    authenticated_user.ip_address = user.ip_address
    # Преобразуем device_time в формат без временной зоны, если необходимо
    authenticated_user.device_time = user.device_time.replace(tzinfo=None) if user.device_time.tzinfo else user.device_time
    authenticated_user.latitude = user.latitude
    authenticated_user.longitude = user.longitude
    
    # Сохраняем обновленную информацию о пользователе
    await db.commit()
    await db.refresh(authenticated_user)

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




@router.post("/confirm-email", dependencies=[Depends(verify_api_key)])
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





@router.post("/refresh", response_model=Token, dependencies=[Depends(verify_api_key)])
async def refresh_token(refresh: TokenRefresh, db: AsyncSession = Depends(get_db)):
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    try:
        # Логирование входящего refresh токена
        print("Received refresh token:", refresh.refresh_token)
        
        # Декодируем токен вручную с использованием библиотеки jwt
        payload = jwt.decode(refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])        
 
        
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





@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_route(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)):
    if credentials is None:
        print("No credentials provided")
        raise HTTPException(status_code=401, detail="No credentials provided")

    user_info = credentials.subject
    print(f"User info extracted from token: {user_info}")
    return {"message": f"Hello {user_info['username']}!"}









@router.get("/profile", response_model=UserProfile, dependencies=[Depends(verify_api_key)])
async def get_profile(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer), db: AsyncSession = Depends(get_db)):
    # Извлекаем данные из токена
    user_info = credentials.subject  # Получаем данные из subject
    print(f"User info extracted from token in /profile: {user_info}")

    user_id = user_info.get("id")  # Предполагается, что subject — это словарь с user_id и username
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token does not contain user ID")

    # Ищем пользователя в базе данных
    user_crud = UserCRUD(db)
    user = await user_crud.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number
    )