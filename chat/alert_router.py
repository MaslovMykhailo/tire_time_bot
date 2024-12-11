import logging

from aiogram import Bot, Router
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from weather_forecast import WeatherForecastAPI, get_tire_type_by_avg_temperature
from database import (
    DBSession,
    Alert,
    get_alerts_to_check,
    get_alerts_to_resend,
    update_tire_type,
    increment_alert_counter,
)

from .messages import ChatMessages
from .helpers import get_chat_location, is_alert_expired

logger = logging.getLogger(__name__)

alert_router = Router(name=__name__)


WEATHER_FORECAST_DAYS = 7


def check_for_alerts_factory(
    bot: Bot,
    messages: ChatMessages,
    weather_forecast_api: WeatherForecastAPI,
    db_session: DBSession,
):
    send_alert = send_alert_factory(bot, messages, db_session)

    async def check_for_alerts():
        async_session = await db_session()

        async for alert in get_alerts_to_check(async_session):
            chat = alert.chat

            avg_temperature = await weather_forecast_api.get_avg_temperature(
                get_chat_location(chat), WEATHER_FORECAST_DAYS
            )
            tire_type = get_tire_type_by_avg_temperature(avg_temperature)

            if tire_type == chat.tire_type:
                continue

            await send_alert(alert, avg_temperature)

        async for alert in get_alerts_to_resend(async_session):
            await send_alert(alert)

    return check_for_alerts


def send_alert_factory(
    bot: Bot,
    messages: ChatMessages,
    db_session: DBSession,
):
    async def send_alert(alert: Alert, avg_temperature: float | None = None):
        try:
            await bot.send_message(
                alert.chat.id,
                messages.alert_change_tire_type(alert.type, alert.count, avg_temperature),
                disable_notification=True,
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(
                                text=messages.alert_notify_stop_button(),
                            ),
                            KeyboardButton(
                                text=messages.alert_notify_again_button(),
                            ),
                        ]
                    ],
                    resize_keyboard=True,
                ),
            )

            async_session = await db_session()

            if is_alert_expired(alert):
                await update_tire_type(async_session, alert.chat_id)
            else:
                await increment_alert_counter(async_session, alert.id)

        except Exception as e:
            logger.exception(e)

    return send_alert


@alert_router.message()
async def handle_alert_reaction(message: Message, messages: ChatMessages, db_session: DBSession) -> None:
    if message.text == messages.alert_notify_stop_button():
        await update_tire_type(await db_session(), message.chat.id)
        await message.answer(messages.alert_notify_stop_confirm(), reply_markup=ReplyKeyboardRemove())
        return

    if message.text == messages.alert_notify_again_button():
        await message.answer(messages.alert_notify_again_confirm(), reply_markup=ReplyKeyboardRemove())
        return
