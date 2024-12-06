from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import Token
from .abstract_cruds import AbstractTokenCRUD


class TokenCRUD(AbstractTokenCRUD):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_tokens_to_db(self, user_id: int, access_token: str, refresh_token: str) -> Token:
        stmt = select(Token).filter_by(user_id=user_id)
        result = await self.db.execute(stmt)
        token_record = result.scalars().first()

        if token_record:
            token_record.access_token = access_token
            token_record.refresh_token = refresh_token
        else:
            token_record = Token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            self.db.add(token_record)

        await self.db.commit()
        await self.db.refresh(token_record)
        return token_record
    
