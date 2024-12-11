from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from weather_forecast import get_opposite_tire_type

from .models import Chat, Alert


async def get_chat_by_id(async_session: async_sessionmaker[AsyncSession], chat_id: int) -> Chat | None:
    async with async_session() as session:
        return await session.get(Chat, chat_id)


async def create_chat(async_session: async_sessionmaker[AsyncSession], chat: Chat) -> None:
    async with async_session() as session:
        session.add(chat)
        await session.commit()


async def create_or_update_chat(async_session: async_sessionmaker[AsyncSession], chat: Chat) -> None:
    async with async_session() as session:
        chat_entity = await session.get(Chat, chat.id)

        if chat_entity is None:
            return await create_chat(async_session, chat)

        chat_entity.lat = chat.lat
        chat_entity.lon = chat.lon
        chat_entity.tire_type = chat.tire_type
        chat_entity.alert.type = chat.alert.type
        chat_entity.alert.count = chat.alert.count

        await session.commit()


async def get_alerts_to_check(async_session: async_sessionmaker[AsyncSession]) -> AsyncIterator[Alert]:
    async with async_session() as session:
        alerts = await session.execute(select(Alert).where(Alert.count == 0))
        for alert in alerts.scalars():
            yield alert


async def get_alerts_to_resend(async_session: async_sessionmaker[AsyncSession]) -> AsyncIterator[Alert]:
    async with async_session() as session:
        alerts = await session.execute(select(Alert).where(Alert.count > 0))
        for alert in alerts.scalars():
            yield alert


async def increment_alert_counter(async_session: async_sessionmaker[AsyncSession], alert_id: int) -> None:
    async with async_session() as session:
        alert = await session.get(Alert, alert_id)

        if alert is None:
            return

        alert.count += 1
        await session.commit()


async def update_tire_type(async_session: async_sessionmaker[AsyncSession], chat_id: int) -> None:
    async with async_session() as session:
        chat = await session.get(Chat, chat_id)

        if chat is None:
            return

        chat.tire_type = get_opposite_tire_type(chat.tire_type)
        chat.alert.type = chat.tire_type
        chat.alert.count = 0
        await session.commit()
