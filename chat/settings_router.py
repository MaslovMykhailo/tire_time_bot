from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from location import LocationAPI, parse_coordinates
from weather_forecast import WeatherForecastAPI, get_tire_type_by_avg_temperature, get_opposite_tire_type
from database import DBSession, Chat

from .messages import ChatMessages

settings_router = Router()


class Settings(StatesGroup):
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
async def command_start_handler(message: Message, state: FSMContext, messages: ChatMessages) -> None:
    # TODO: check if the user already has location set
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
    place_name = await location_api.get_place_name(location)

    if location is None or place_name is None:
        await message.answer(messages.settings_location_coordinates_invalid())
        return

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


# TODO: implement the place location setting
# @settings_router.message(Settings.location, F.text.casefold() == LocationSettingType.Place)
# async def process_location_with_place(message: Message, state: FSMContext) -> None:
#     await state.set_state(Settings.place_location)
#     await message.answer(
#         "Enter the name of the settlement",
#         reply_markup=ReplyKeyboardRemove(),
#     )


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


@settings_router.message(Settings.location_confirmation, F.text.casefold() == Confirmation.No)
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


@settings_router.message(Settings.tire_type_confirmation, F.text.casefold() == Confirmation.Yes)
async def process_tire_type_confirmation(
    message: Message, state: FSMContext, messages: ChatMessages, db_session: DBSession
) -> None:
    data = await state.get_data()
    tire_type = data["tire_type"]
    location = data["location"]

    if message.text.casefold() == Confirmation.No:
        tire_type = get_opposite_tire_type(tire_type)

    async_session = await db_session()
    async with async_session() as session:
        async with session.begin():
            # TODO: handle the case when the chat already exists
            session.add(
                Chat(id=message.chat.id, lat=location["lat"], lon=location["lon"], tire_type=tire_type, alerts=[])
            )

    await message.answer(messages.settings_tire_type_set(tire_type), reply_markup=ReplyKeyboardRemove())
