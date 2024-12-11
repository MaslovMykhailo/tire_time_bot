import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from chat import settings_router, alert_router, ChatMessages
from location import NominatimAPI
from weather_forecast import WeatherAPI
from database import DBEngine

load_dotenv(override=True)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DB_URL = os.getenv("DB_URL")


async def task(check_for_alerts):
    while True:
        await check_for_alerts()
        await asyncio.sleep(60)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    messages = ChatMessages()
    location_api = NominatimAPI()
    weather_forecast_api = WeatherAPI(WEATHER_API_KEY)

    db_engine = DBEngine(DB_URL)
    await db_engine.create_all()

    dp = Dispatcher(
        location_api=location_api,
        weather_forecast_api=weather_forecast_api,
        db_session=db_engine.get_db_session,
        messages=messages,
    )
    dp.include_router(settings_router)
    dp.include_router(alert_router)

    await dp.start_polling(bot)
    await db_engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
