from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .models import Chat


async def getChatById(async_session: async_sessionmaker[AsyncSession], id: int) -> Chat | None:
    async with async_session() as session:
        return await session.get(Chat, id)
