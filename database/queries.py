from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .models import Chat


async def getChatById(async_session: async_sessionmaker[AsyncSession], id: int) -> Chat | None:
    async with async_session() as session:
        return await session.get(Chat, id)


async def createChat(async_session: async_sessionmaker[AsyncSession], chat: Chat) -> None:
    async with async_session() as session:
        session.add(chat)


async def createOrUpdateChat(async_session: async_sessionmaker[AsyncSession], chat: Chat) -> None:
    async with async_session() as session:
        existedChat = await session.get(Chat, chat.id)

        if existedChat is None:
            return await createChat(async_session, chat)

        existedChat.lat = chat.lat
        existedChat.lon = chat.lon
        existedChat.tire_type = chat.tire_type

        for alert in existedChat.alerts:
            session.delete(alert)

        for alert in chat.alerts:
            session.add(alert)
