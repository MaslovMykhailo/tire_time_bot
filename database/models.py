from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


# When user submits location, the chat id, current tire type and coordinates are saved in the database.
#
# The bot should check the weather once a day and schedule alert of needed type when the weather changes.
# The alert should be scheduled only when there are no other alerts for the same chat.
# The alert counter changes every time when the alert is shown to the user.
# When alert counter reaches 3, the alert is removed from the database and tire type is changed automatically.
#
# If the user react on alert, submits tire type change, then the alert should be removed from the database.
# When the user changes current tire type, the alert should be removed from the database.


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)

    lat: Mapped[float] = mapped_column()
    lon: Mapped[float] = mapped_column()

    tire_type: Mapped[int] = mapped_column()
    formatted_tire_type = {
        0: "winter",
        1: "summer",
    }

    alerts: Mapped[List["Alert"]] = relationship(back_populates="chat", lazy="selectin")

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, [lat={self.latitude!r}, lon={self.fullname!r}])"


class Alert(Base):
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="alerts", lazy="selectin")

    type: Mapped[int] = mapped_column()
    formatted_type = {
        0: "winter to summer",
        1: "summer to winter",
    }

    count: Mapped[Optional[int]] = mapped_column()

    def __repr__(self) -> str:
        type = self.formatted_type[self.type]
        return f"Alert(id={self.id!r}, chat_id={self.chat_id!r}, type={type!r} count={self.count!r})"
