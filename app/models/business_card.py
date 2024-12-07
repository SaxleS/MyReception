from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class BusinessCard(Base):
    __tablename__ = "business_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subdomain = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    links = Column(String, nullable=True)