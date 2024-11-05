from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .models import Base

type DBSession = async_sessionmaker[AsyncSession]


class DBEngine:

    engine: AsyncEngine

    def __init__(self, db_url: str) -> None:
        print(db_url)
        self.engine = create_async_engine(db_url, echo=True)

    async def create_all(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def get_db_session(self) -> DBSession:
        return async_sessionmaker(self.engine, expire_on_commit=False)
