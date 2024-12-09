from fastapi import Depends
from app.services.chat_service.chat_service import ChatService

def get_chat_service() -> ChatService:
    """Фабрика для получения экземпляра ChatService"""
    return ChatService()