import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from chat import settings_router, alert_router, ChatMessages, check_for_alerts_factory
from location import NominatimAPI
from weather_forecast import WeatherAPI
from database import DBEngine

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


def start_alerts_scheduler(check_for_alerts):
    scheduler = AsyncIOScheduler()
    # Schedule the job to run daily at 9:00 AM
    scheduler.add_job(check_for_alerts, CronTrigger(hour=9, minute=0))
    scheduler.start()


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    messages = ChatMessages()
    location_api = NominatimAPI()
    weather_forecast_api = WeatherAPI(WEATHER_API_KEY)

    db_engine = DBEngine(DATABASE_URL)
    await db_engine.create_all()

    dp = Dispatcher(
        location_api=location_api,
        weather_forecast_api=weather_forecast_api,
        db_session=db_engine.get_db_session,
        messages=messages,
    )
    dp.include_router(settings_router)
    dp.include_router(alert_router)

    start_alerts_scheduler(
        check_for_alerts_factory(
            bot,
            messages,
            weather_forecast_api,
            db_session=db_engine.get_db_session,
        )
    )

    await dp.start_polling(bot)
    await db_engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
