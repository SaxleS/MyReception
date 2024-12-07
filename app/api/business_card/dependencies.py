# app/api/dependencies.py
from app.crud.business_card.business_card_crud import BusinessCardCRUD
from app.services.business_card.business_card_service import BusinessCardService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_db

def get_business_card_service(db: AsyncSession = Depends(get_db)) -> BusinessCardService:
    crud = BusinessCardCRUD(db)
    return BusinessCardService(crud=crud)