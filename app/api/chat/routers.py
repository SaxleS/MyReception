from fastapi import APIRouter, Depends, HTTPException, status
from app.services.chat_service import ChatService
from typing import List, Dict, Union
from pydantic import BaseModel
from app.core.security import JWTAuth

from app.logs.logger import Logger  

logger = Logger.setup_logger()



class CreateChatRequest(BaseModel):
    participants: List[Union[int, str]]  # Список участников (ID авторизованных пользователей или уникальные идентификаторы анонимных).


class SendMessageRequest(BaseModel):
    sender_id: Union[int, str]  # ID отправителя (авторизованный или анонимный).
    message: str


def get_chat_router() -> APIRouter:
    router = APIRouter()
    jwt_auth = JWTAuth()

    @router.post("/chats/", response_model=Dict, status_code=status.HTTP_201_CREATED)
    async def create_chat(
        request: CreateChatRequest,
        current_user_id: int = Depends(jwt_auth.get_current_user_id),
        chat_service: ChatService = Depends(),
    ):
        """
        Создать чат с указанными участниками, включая текущего пользователя.
        """
        participants = list(set(request.participants + [current_user_id]))
        
        if not participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Participants cannot be empty.",
            )

        if not all(
            isinstance(p, int) or (isinstance(p, str) and p.startswith("anon_"))
            for p in participants
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Participants must be user IDs (int) or anonymous IDs starting with 'anon_'.",
            )

        try:
            return await chat_service.create_chat(participants)
        except ValueError as e:
            logger.error(f"ValueError: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error.",
            )

    @router.post("/chats/{chat_id}/messages/", response_model=Dict, status_code=status.HTTP_201_CREATED)
    async def send_message(
        chat_id: str,
        request: SendMessageRequest,
        current_user_id: int = Depends(jwt_auth.get_current_user_id),
        chat_service: ChatService = Depends(),
    ):
        """
        Отправить сообщение в указанный чат.
        """
        try:
            chat = await chat_service.get_chat(chat_id)
            if not chat or current_user_id not in chat["participants"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to send messages in this chat.",
                )

            return await chat_service.add_message(chat_id, request.sender_id, request.message)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending message.",
            )

    @router.post("/chats/{chat_id}/messages/view/", response_model=List[Dict], status_code=status.HTTP_200_OK)
    async def get_chat_messages(
        chat_id: str,
        current_user_id: int = Depends(jwt_auth.get_current_user_id),
        chat_service: ChatService = Depends(),
    ):
        """
        Получить сообщения из указанного чата. Только для участников.
        """
        try:
            chat = await chat_service.get_chat(chat_id)
            if not chat or current_user_id not in chat["participants"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to this chat is denied.",
                )
            return await chat_service.get_messages(chat_id)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching messages.",
            )

    @router.post("/chats/start_by_name/", response_model=Dict, status_code=status.HTTP_201_CREATED)
    async def start_chat_by_name(
        username: str,
        current_user_id: int = Depends(jwt_auth.get_current_user_id),
        chat_service: ChatService = Depends(),
    ):
        """
        Начать чат с пользователем, найденным по имени.
        """
        try:
            target_user_id = await chat_service.get_user_id_by_username(username)
            if not target_user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with username '{username}' not found.",
                )

            participants = [current_user_id, target_user_id]
            return await chat_service.create_chat(participants)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not start chat.",
            )

    @router.get("/chats/", response_model=List[Dict], status_code=status.HTTP_200_OK)
    async def get_user_chats(
        current_user_id: int = Depends(jwt_auth.get_current_user_id),
        chat_service: ChatService = Depends(),
    ):
        """
        Получить список чатов текущего пользователя.
        """
        try:
            return await chat_service.get_chats_by_user(current_user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch user chats.",
            )

    return router


router = get_chat_router()