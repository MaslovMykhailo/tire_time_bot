from database import Chat, Alert
from location import Location


def get_chat_location(chat: Chat) -> Location:
    return Location(lat=chat.lat, lon=chat.lon)


ALERT_EXPIRATION_COUNT = 3


def is_alert_expired(alert: Alert) -> bool:
    return alert.count >= ALERT_EXPIRATION_COUNT
