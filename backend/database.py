import contextlib
from typing import Any, AsyncIterator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine, async_sessionmaker

from backend.settings import settings
from models.weather import Base


class DatabaseSessionManager:
    # Create all necessary handlers for database connection
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}, expire_on_commit: bool = True, test_db=False):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=expire_on_commit)

        # Enable foreign key support for SQLite
        @event.listens_for(self._engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()


sessionmanager = DatabaseSessionManager(settings.database_url, {"echo": settings.echo_sql})
test_sessionmanager = DatabaseSessionManager(settings.test_database_url, {"echo": settings.echo_test_sql}, expire_on_commit=False, test_db=True)

async def db_session():
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with sessionmanager.session() as session:
        yield session
