import asyncio
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Tuple
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from module.core.tools.log import logger
from module.core.tools.settings import app_settings, Settings


class PSQLManager:
    def __init__(self):
        self.db_engine: Optional[AsyncEngine] = None
        self.session_maker = None
        self.is_sqlite_fallback = False

    def get_engine(self, setting: Settings) -> AsyncEngine:
        """
        Retrieves or instantiates the database configuration engine.
        Does NOT execute blocking network pings on creation.
        """
        if self.db_engine is not None:
            return self.db_engine

        if setting.DATABASE_URL is None:
            raise ValueError("Database URL must be provided for initialization.")

        connect_args = {}
        if "postgresql" in setting.DATABASE_URL:
            # Fixed key for asyncpg driver matching
            connect_args = {"timeout": 10}

        logger.info(f"Configuring primary DB engine layer: {setting.DATABASE_URL}")
        self.db_engine = create_async_engine(
            setting.DATABASE_URL,
            echo=True,
            connect_args=connect_args
        )
        self.is_sqlite_fallback = False
        return self.db_engine

    async def initialize_and_verify(self, setting: Settings) -> AsyncEngine:
        """
        Asynchronously verifies the health of the primary database connection.
        Retries up to 3 times with a 5-second interval between attempts.
        Safely switches over to SQLite within a 3.0-second threshold if all retries fail.
        Call this function inside the active ASGI event loop runtime lifecycle (Lifespan).
        """
        engine = self.get_engine(setting)

        if self.is_sqlite_fallback:
            return self.db_engine

        max_retries = 3
        retry_delay = 5.0

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Pinging primary database to verify real network connectivity... (Attempt {attempt}/{max_retries})")

                # Enforces network boundary execution context safely
                await asyncio.wait_for(self._ping_database(engine), timeout=3.0)

                # Setup the sessionmaker for Postgres since connection passed
                self.get_session_maker(setting)
                logger.info("Primary Database connection verified successfully.")
                return self.db_engine

            except Exception as e:
                logger.warning(f"Database connection attempt {attempt} failed: {e}")

                # If we have remaining retries, wait before next attempt
                if attempt < max_retries:
                    logger.info(f"Waiting {retry_delay} seconds before retrying...")
                    await asyncio.sleep(retry_delay)
                else:
                    # All retries exhausted, proceed to fallback
                    logger.error("All 3 primary DB connection attempts failed. Falling back to SQLite immediately...")
                    self.db_engine = None
                    self.session_maker = None
                    self._setup_sqlite(setting)
                    self.get_session_maker(setting)

        return self.db_engine

    async def _ping_database(self, engine: AsyncEngine):
        """Executes a lightweight driver-level SQL statement to check network sanity."""
        async with engine.connect() as conn:
            # Use raw driver-level query to bypass costly ORM layers
            await conn.exec_driver_sql("SELECT 1")

    def _setup_sqlite(self, setting: Settings):
        """Configures the fallback SQLite in-memory or file-based database."""
        logger.info(f"Initializing fallback SQLite engine: {setting.FALLBACK_DATABASE_URL}")
        self.db_engine = create_async_engine(
            setting.FALLBACK_DATABASE_URL,
            echo=True,
            connect_args={"check_same_thread": False}
        )
        self.is_sqlite_fallback = True

    def get_session_maker(self, setting: Optional[Settings] = None):
        if self.session_maker is not None:
            return self.session_maker

        if self.db_engine is None:
            self._setup_sqlite(setting or app_settings)

        self.session_maker = sessionmaker(
            self.db_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        return self.session_maker

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.db_engine is None:
            self.get_engine(app_settings)

        session_maker = self.get_session_maker(app_settings)
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_db_session_and_engine(self) -> AsyncGenerator[Tuple[AsyncSession, AsyncEngine], None]:
        if self.db_engine is None:
            self.get_engine(app_settings)

        session_maker = self.get_session_maker(app_settings)
        async with session_maker() as session:
            try:
                yield session, self.db_engine
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close_pool(self) -> None:
        if self.db_engine is not None:
            logger.info("Closing primary database engine connection pool...")
            await self.db_engine.dispose()
            self.db_engine = None
            self.session_maker = None
            logger.info("Database connection pool closed successfully.")


psql_manager = PSQLManager()


def db_session_manager(func):
    async def inner_function(*args, **kwargs):
        async with psql_manager.get_db_session() as db_session:
            try:
                kwargs["db_session"] = db_session
                result = await func(*args, **kwargs)
                await db_session.commit()
                return result
            except Exception as e:
                await db_session.rollback()
                raise e

    return inner_function