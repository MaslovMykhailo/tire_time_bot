from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from location import LocationAPI, parse_coordinates
from weather_forecast import WeatherForecastAPI, get_tire_type_by_avg_temperature, get_opposite_tire_type
from database import DBSession, Chat, Alert, get_chat_by_id, create_or_update_chat

from .messages import ChatMessages
from .helpers import get_chat_location

settings_router = Router(name=__name__)


class Settings(StatesGroup):
    configure = State()

    location = State()
    coordinates_location = State()
    place_location = State()

    location_confirmation = State()
    tire_type_confirmation = State()


class LocationSettingType:
    Coordinates = "coordinates"
    Place = "place"


class Confirmation:
    Yes = "yes"
    No = "no"


@settings_router.message(CommandStart())
async def command_start_handler(
    message: Message, state: FSMContext, messages: ChatMessages, location_api: LocationAPI, db_session: DBSession
) -> None:
    chat = await get_chat_by_id(await db_session(), message.chat.id)

    if chat is not None:
        await state.set_state(Settings.configure)

        place_name = await location_api.get_place_name(get_chat_location(chat))
        await message.answer(
            messages.settings_start_configured_chat(place_name, chat.tire_type),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=messages.settings_configure_button())]], resize_keyboard=True
            ),
        )

        return

    await state.set_state(Settings.location)
    await message.answer(
        messages.settings_start(),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=LocationSettingType.Coordinates.capitalize()),
                    KeyboardButton(text=LocationSettingType.Place.capitalize()),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@settings_router.message(Command("settings"))
async def command_settings_handler(
    message: Message, state: FSMContext, messages: ChatMessages, location_api: LocationAPI, db_session: DBSession
) -> None:
    await state.set_state(Settings.configure)

    chat = await get_chat_by_id(await db_session(), message.chat.id)

    if chat is None:
        await message.answer(
            messages.settings_overview_not_configured_chat(),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=messages.settings_configure_button())]], resize_keyboard=True
            ),
        )
        return

    place_name = await location_api.get_place_name(get_chat_location(chat))
    await message.answer(
        messages.settings_overview(place_name, chat.tire_type),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=messages.settings_configure_button())]], resize_keyboard=True
        ),
    )


@settings_router.message(Settings.configure)
async def process_configure_settings(message: Message, state: FSMContext, messages: ChatMessages) -> None:
    if not message.text.casefold() == messages.settings_configure_button().casefold():
        await state.clear()
        await message.answer(messages.settings_change_settings_keep_current(), reply_markup=ReplyKeyboardRemove())
        return

    await state.set_state(Settings.location)
    await message.answer(
        messages.settings_location(),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=LocationSettingType.Coordinates.capitalize()),
                    KeyboardButton(text=LocationSettingType.Place.capitalize()),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@settings_router.message(Settings.location, F.text.casefold() == LocationSettingType.Coordinates)
async def process_location_with_coordinates(message: Message, state: FSMContext, messages: ChatMessages) -> None:
    await state.set_state(Settings.coordinates_location)
    await message.answer(
        messages.settings_location_coordinates(),
        reply_markup=ReplyKeyboardRemove(),
    )


@settings_router.message(Settings.coordinates_location)
async def process_coordinates_location(
    message: Message, state: FSMContext, messages: ChatMessages, location_api: LocationAPI
) -> None:
    raw_coordinates = message.text.strip()
    location = parse_coordinates(raw_coordinates)

    if location is None:
        await message.answer(messages.settings_location_coordinates_invalid())
        return

    place_name = await location_api.get_place_name(location)

    await state.update_data(location=location)
    await state.set_state(Settings.location_confirmation)

    await message.answer(
        messages.settings_location_confirmation(place_name),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=Confirmation.Yes.capitalize()), KeyboardButton(text=Confirmation.No.capitalize())]
            ],
            resize_keyboard=True,
        ),
    )


@settings_router.message(Settings.location, F.text.casefold() == LocationSettingType.Place)
async def process_location_with_place(message: Message, state: FSMContext, messages: ChatMessages) -> None:
    await state.set_state(Settings.place_location)
    await message.answer(
        messages.settings_location_place(),
        reply_markup=ReplyKeyboardRemove(),
    )


@settings_router.message(Settings.place_location)
async def process_place_location(
    message: Message, state: FSMContext, messages: ChatMessages, location_api: LocationAPI
) -> None:
    location = await location_api.search(message.text.strip())

    if location is None:
        await message.answer(messages.settings_location_place_not_found(), reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(location=location)
    await state.set_state(Settings.location_confirmation)

    place_name = await location_api.get_place_name(location)
    await message.answer(
        messages.settings_location_confirmation(place_name),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=Confirmation.Yes.capitalize()), KeyboardButton(text=Confirmation.No.capitalize())]
            ],
            resize_keyboard=True,
        ),
    )


@settings_router.message(Settings.location_confirmation, F.text.casefold() == Confirmation.Yes)
async def process_location_confirmation_agreement(
    message: Message, state: FSMContext, messages: ChatMessages, weather_forecast_api: WeatherForecastAPI
) -> None:
    data = await state.get_data()

    location = data["location"]
    avg_temperature = await weather_forecast_api.get_avg_temperature(location, 1)
    tire_type = get_tire_type_by_avg_temperature(avg_temperature)

    await state.update_data(tire_type=tire_type)
    await state.set_state(Settings.tire_type_confirmation)
    await message.answer(
        messages.settings_tire_type_confirmation(avg_temperature, tire_type),
        keyboard=[
            [KeyboardButton(text=Confirmation.Yes.capitalize()), KeyboardButton(text=Confirmation.No.capitalize())]
        ],
        resize_keyboard=True,
    )


@settings_router.message(Settings.location_confirmation)
async def process_location_confirmation_disagreement(
    message: Message, state: FSMContext, messages: ChatMessages
) -> None:
    await state.set_state(Settings.location)
    await message.answer(
        messages.settings_location(),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=LocationSettingType.Coordinates.capitalize()),
                    KeyboardButton(text=LocationSettingType.Place.capitalize()),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@settings_router.message(Settings.tire_type_confirmation)
async def process_tire_type_confirmation(
    message: Message, state: FSMContext, messages: ChatMessages, db_session: DBSession
) -> None:
    data = await state.get_data()
    tire_type = data["tire_type"]
    location = data["location"]

    if message.text.casefold() == Confirmation.No:
        tire_type = get_opposite_tire_type(tire_type)

    chat = Chat(
        id=message.chat.id,
        lat=location["lat"],
        lon=location["lon"],
        tire_type=tire_type,
        alert=Alert(chat_id=message.chat.id, type=tire_type, count=0),
    )
    await create_or_update_chat(await db_session(), chat)

    await state.clear()
    await message.answer(messages.settings_tire_type_set(tire_type), reply_markup=ReplyKeyboardRemove())
