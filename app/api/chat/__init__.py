from fastapi import APIRouter
from .routers import router as user_router  # Импортируем router из файла routers.py

api_router = APIRouter()
api_router.include_router(user_router, prefix="/chat", tags=["chat"])