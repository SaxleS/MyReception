# app/services/business_card/business_card_service.py
from typing import Optional
from app.services.business_card.abstract_business_card_service import AbstractBusinessCardService
from app.schemas.business_card import BusinessCardCreate, BusinessCardResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.business_card.business_card_crud import BusinessCardCRUD


class BusinessCardService(AbstractBusinessCardService):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crud = BusinessCardCRUD(db)

    async def create_or_update_card(self, user_id: int, data: BusinessCardCreate) -> BusinessCardResponse:
        """
        Создаёт или обновляет бизнес-карточку пользователя.

        :param user_id: ID пользователя.
        :param data: Данные для создания/обновления карточки.
        :return: Объект BusinessCardResponse.
        """
        card = await self.crud.get_card_by_user_id(user_id)
        if card:
            updated_card = await self.crud.update_card(user_id, data)
            return BusinessCardResponse(**updated_card.dict())
        new_card = await self.crud.create_or_update_card(user_id, data)
        return BusinessCardResponse(**new_card.dict())

    async def get_card(self, user_id: int) -> Optional[BusinessCardResponse]:
        """
        Получает карточку пользователя по его ID.

        :param user_id: ID пользователя.
        :return: Объект BusinessCardResponse или None.
        """
        card = await self.crud.get_card_by_user_id(user_id)
        if card:
            return BusinessCardResponse(**card.dict())
        return None

    async def get_card_by_subdomain(self, subdomain: str) -> Optional[BusinessCardResponse]:
        """
        Получает карточку по поддомену.

        :param subdomain: Поддомен карточки.
        :return: Объект BusinessCardResponse или None.
        """
        card = await self.crud.get_card_by_url(subdomain)
        if card:
            return BusinessCardResponse(**card.dict())
        return None