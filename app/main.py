from fastapi import FastAPI, Depends, HTTPException, Header, status


from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from pydantic import BaseModel
from datetime import timedelta


from app.api.users.routers import router as user_router
from app.core.security import JWTAuth, jwt_bearer, verify_api_key, SECRET_KEY, API_KEY
from app.core.config import app



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
# app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(user_router, prefix="/api/v1", tags=["Users / Authorization"], dependencies=[Depends(verify_api_key)])



