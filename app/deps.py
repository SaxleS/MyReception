from fastapi import Depends, HTTPException
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from pydantic import BaseModel
from datetime import timedelta

# Инициализация JWT
jwt_bearer = JwtAccessBearer(secret_key="supersecretkey")

class Settings(BaseModel):
    authjwt_secret_key: str = "supersecretkey"
    authjwt_access_token_expires: int = 15  # Время жизни access token в минутах
    authjwt_refresh_token_expires: int = 1440  # Время жизни refresh token в минутах

def get_current_user(credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)):
    try:
        # Проверка токена
        current_user = credentials.subject  # Получаем информацию из токена
        return current_user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Пример создания токена
def create_access_token(username: str):
    access_token = jwt_bearer.create_access_token(
        subject=username,
        expires_delta=timedelta(minutes=Settings().authjwt_access_token_expires)
    )
    return access_token