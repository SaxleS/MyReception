from app.api.chat.abstract_apis import AbstractChatAPI
from app.services.chat_service.abstract_chat_service import AbstractChatService  # Импортируем абстрактный класс
from typing import List, Dict

class ChatAPI(AbstractChatAPI):
    def __init__(self, chat_service: AbstractChatService):  # Используем абстрактный класс
        """
        Инициализация ChatAPI с внедрением зависимости AbstractChatService.
        :param chat_service: Сервис для работы с чатами.
        """
        self.chat_service = chat_service

    async def create_chat(self, participants: List[int]) -> Dict:
        """
        Создание нового чата.
        :param participants: Список участников чата.
        :return: Словарь с идентификатором чата.
        """
        return await self.chat_service.create_chat(participants)

    async def send_message(self, chat_id: str, sender_id: int, message: str) -> Dict:
        """
        Отправка сообщения в чат.
        :param chat_id: Идентификатор чата.
        :param sender_id: Идентификатор отправителя.
        :param message: Текст сообщения.
        :return: Словарь со статусом отправки.
        """
        return await self.chat_service.add_message(chat_id, sender_id, message)

    async def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """
        Получение всех сообщений из чата.
        :param chat_id: Идентификатор чата.
        :return: Список сообщений.
        """
        return await self.chat_service.get_messages(chat_id)