from app.core.database import mongodb
from bson.objectid import ObjectId
from typing import List, Dict, Union
from pymongo.errors import PyMongoError

from app.services.chat_service.abstract_chat_service import AbstractChatService


class ChatService(AbstractChatService):
    async def create_chat(self, participants: List[Union[int, str]]) -> Dict:
        """
        Создает новый чат с участниками. Убирает дубли участников.
        """
        if not participants:
            raise ValueError("Chat must have at least one participant.")
        
        participants = list(set(participants))  # Удаляем дубли

        try:
            if mongodb.db is None:
                raise ValueError("MongoDB connection is not initialized.")
            
            chat_data = {"participants": participants, "messages": []}
            result = await mongodb.db["chats"].insert_one(chat_data)
            return {"chat_id": str(result.inserted_id)}
        except PyMongoError as e:
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    async def add_message(self, chat_id: str, sender_id: Union[int, str], message: str) -> Dict:
        """
        Добавляет сообщение в чат.
        """
        if not message.strip():
            raise ValueError("Message cannot be empty.")

        chat = await mongodb.db["chats"].find_one({"_id": ObjectId(chat_id)})
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} not found.")

        message_data = {"sender_id": sender_id, "message": message}
        update_result = await mongodb.db["chats"].update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": message_data}}
        )
        if update_result.modified_count == 0:
            raise ValueError("Failed to add message to chat.")
        
        return {"status": "message sent"}

    async def get_messages(self, chat_id: str) -> List[Dict]:
        """
        Получает список сообщений из чата.
        """
        chat = await mongodb.db["chats"].find_one({"_id": ObjectId(chat_id)})
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} not found.")
        return chat["messages"]

    async def get_chats_by_user(self, user_id: Union[int, str]) -> List[Dict]:
        """
        Возвращает список чатов, в которых участвует пользователь.
        """
        chats = await mongodb.db["chats"].find({"participants": user_id}).to_list(length=None)
        return [{"chat_id": str(chat["_id"]), "participants": chat["participants"]} for chat in chats]

    async def get_user_id_by_username(self, username: str) -> Union[int, None]:
        """
        Находит ID пользователя по имени.
        """
        user = await mongodb.db["users"].find_one({"username": username})
        return user["id"] if user else None