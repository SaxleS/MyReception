from app.core.database import mongodb
from bson.objectid import ObjectId
from typing import List, Dict

class MessageService:
    async def save_message(self, chat_id: str, sender_id: int, message: str) -> Dict:
        message_data = {"chat_id": chat_id, "sender_id": sender_id, "message": message}
        result = await mongodb.db["messages"].insert_one(message_data)
        return {"message_id": str(result.inserted_id)}

    async def get_chat_messages(self, chat_id: str) -> List[Dict]:
        messages = await mongodb.db["messages"].find({"chat_id": chat_id}).to_list(100)
        return messages