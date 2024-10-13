from fastapi import APIRouter
from teleport_webrtc.api import users, tasks  # Импортируйте transactions

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
