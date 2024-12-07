# app/crud/business_card/business_card_crud.py
from app.models.business_card import BusinessCard
from app.schemas.business_card import BusinessCardCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.crud.business_card.abstract_business_card_crud import AbstractBusinessCardCRUD

class BusinessCardCRUD(AbstractBusinessCardCRUD):
    async def create_or_update_card(self, user_id: int, data: BusinessCardCreate) -> BusinessCard:
        stmt = select(BusinessCard).where(BusinessCard.user_id == user_id)
        result = await self.db.execute(stmt)
        card = result.scalars().first()

        if card:
            card.title = data.title
            card.description = data.description
        else:
            card = BusinessCard(user_id=user_id, title=data.title, description=data.description, url=f"card/{user_id}")
            self.db.add(card)

        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def get_card_by_user_id(self, user_id: int) -> Optional[BusinessCard]:
        stmt = select(BusinessCard).where(BusinessCard.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()