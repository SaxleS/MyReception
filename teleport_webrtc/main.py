from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from teleport_webrtc.api import users, tasks
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from pydantic import BaseModel
from datetime import timedelta


import os
from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearer

# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретный ключ из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY")








app = FastAPI(
    title="teleport_webrtc_api",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)

class User(BaseModel):
    username: str
    password: str



@app.get("/protected", tags=["Protected"])
def protected(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)):
    return {"user": credentials.subject}

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "teleport webrtc"}

# Подключение роутера для пользователей
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])

# Запуск приложения: uvicorn teleport_webrtc.main:app --reload