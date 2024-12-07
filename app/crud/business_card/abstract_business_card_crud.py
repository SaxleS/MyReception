from abc import ABC, abstractmethod
from typing import Any, Optional


class AbstractBusinessCardCRUD(ABC):
    """
    Абстрактный класс для CRUD операций с бизнес-карточками.
    """

    @abstractmethod
    async def create_card(self, user_id: int, data: dict) -> Any:
        """
        Создаёт новую бизнес-карточку для пользователя.

        :param user_id: ID пользователя.
        :param data: Данные карточки.
        :return: Созданная карточка.
        """
        pass

    @abstractmethod
    async def get_card_by_subdomain(self, subdomain: str) -> Optional[dict]:
        """
        Возвращает бизнес-карточку по поддомену.

        :param subdomain: Поддомен карточки.
        :return: Данные карточки или None, если не найдена.
        """
        pass

    @abstractmethod
    async def update_card(self, card_id: int, data: dict) -> Any:
        """
        Обновляет существующую бизнес-карточку.

        :param card_id: ID карточки.
        :param data: Данные для обновления.
        :return: Обновлённая карточка.
        """
        pass

    @abstractmethod
    async def delete_card(self, card_id: int) -> None:
        """
        Удаляет бизнес-карточку.

        :param card_id: ID карточки.
        """
        pass


