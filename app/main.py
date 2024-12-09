from fastapi import FastAPI, Depends, HTTPException, Header, status


from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from pydantic import BaseModel
from datetime import timedelta

from app.core.database import mongodb, connect, disconnect
from app.core.security import JWTAuth, jwt_bearer, verify_api_key, SECRET_KEY, API_KEY
from app.core.config import app

from app.api.chat.routers import router as get_chat_router
from app.api.users.routers import router as user_router
from app.api.business_card.routers import router as get_business_card_router



@app.on_event("startup")
async def startup_event():
    await connect()
    await mongodb.connect()
    print("Connected to PostgreSQL and MongoDB")

@app.on_event("shutdown")
async def shutdown_event():
    await disconnect()
    await mongodb.disconnect()
    print("Disconnected from PostgreSQL and MongoDB")




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
app.include_router(get_business_card_router, prefix="/api/v1", tags=["Bisiness Card"], dependencies=[Depends(verify_api_key)])
app.include_router(get_chat_router, prefix="/api/v1", tags=["Chat"], dependencies=[Depends(verify_api_key)])



