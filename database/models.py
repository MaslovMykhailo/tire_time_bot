from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    lat: Mapped[float] = mapped_column()
    lon: Mapped[float] = mapped_column()
    alert: Mapped[List["Alert"]] = relationship(back_populates="chat")

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, [lat={self.latitude!r}, lon={self.fullname!r}])"


class Alert(Base):
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="alert")

    type: Mapped[int] = mapped_column()
    formatted_type = {
        0: "winter to summer",
        1: "summer to winter",
    }

    count: Mapped[Optional[int]] = mapped_column()

    def __repr__(self) -> str:
        type = self.formatted_type[self.type]
        return f"Alert(id={self.id!r}, chat_id={self.chat_id!r}, type={type!r} count={self.count!r})"
