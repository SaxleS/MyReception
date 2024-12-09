from abc import ABC, abstractmethod
from typing import List, Dict, Union


class AbstractChatService(ABC):
    @abstractmethod
    async def create_chat(self, participants: List[Union[int, str]]) -> Dict:
        pass

    @abstractmethod
    async def add_message(self, chat_id: str, sender_id: Union[int, str], message: str) -> Dict:
        pass

    @abstractmethod
    async def get_messages(self, chat_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def get_chats_by_user(self, user_id: Union[int, str]) -> List[Dict]:
        pass