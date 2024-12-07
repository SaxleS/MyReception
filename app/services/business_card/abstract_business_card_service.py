# app/services/business_card/abstract_business_card_service.py
from abc import ABC, abstractmethod
from app.schemas.business_card import BusinessCardCreate, BusinessCardResponse
from typing import Optional


class AbstractBusinessCardService(ABC):
    @abstractmethod
    async def create_or_update_card(self, user_id: int, data: BusinessCardCreate) -> BusinessCardResponse:
        """
        Создаёт или обновляет бизнес-карточку пользователя.

        :param user_id: ID пользователя.
        :param data: Данные для создания/обновления карточки.
        :return: Объект BusinessCardResponse.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_card(self, user_id: int) -> Optional[BusinessCardResponse]:
        """
        Получает карточку пользователя по его ID.

        :param user_id: ID пользователя.
        :return: Объект BusinessCardResponse или None, если карточка не найдена.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_card_by_subdomain(self, subdomain: str) -> Optional[BusinessCardResponse]:
        """
        Получает карточку по поддомену.

        :param subdomain: Поддомен карточки.
        :return: Объект BusinessCardResponse или None, если карточка не найдена.
        """
        raise NotImplementedError