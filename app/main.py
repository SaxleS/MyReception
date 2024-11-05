from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api import users
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from pydantic import BaseModel
from datetime import timedelta
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретные ключи из переменных окружения
SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")

app = FastAPI(
    title="MyReception",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)

class User(BaseModel):
    username: str
    password: str

# Зависимость для проверки API-ключа
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )



@app.get("/protected", tags=["Protected"], dependencies=[Depends(verify_api_key)])
def protected(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)):
    return {"user": credentials.subject}

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "MyReception API",
        "documentation": "/docs",
        "description": "API for managing salon bookings and virtual receptionist services."
    }

# Подключение роутера для пользователей
app.include_router(users.router, prefix="/api/v1", tags=["Users"])