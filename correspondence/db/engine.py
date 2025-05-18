import dataclasses
import threading
import time
import typing as t

from pydantic import PostgresDsn
from sqlalchemy import (Connection, CursorResult, Engine, ExecutionContext,
                        create_engine, event)
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker)
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from .sql import text


@dataclasses.dataclass
class RecordedQuery:
    statement: str | None
    parameters: t.Any
    start_time: float
    end_time: float
    location: str | None = None

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class DatabaseEngine:
    sync_engine: Engine
    async_engine: AsyncEngine
    async_session_local: async_sessionmaker[AsyncSession]
    session_local: sessionmaker[Session]

    def __init__(self, database_url: PostgresDsn):
        self.async_engine = self.create_async_engine(
            dsn=str(database_url),
            debug=False,
        )

        self.sync_engine = create_engine(url=str(database_url))

        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.sync_engine
        )

        event.listen(
            self.async_engine.sync_engine,
            "before_cursor_execute",
            self.before_cursor_execute,
        )
        event.listen(
            self.async_engine.sync_engine,
            "after_cursor_execute",
            self.after_cursor_execute,
        )

        self.async_session_local = async_sessionmaker(
            self.async_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        self.data = threading.local()

    def get_session(self) -> Session:
        return self.session_local()

    async def get_asession(self) -> AsyncSession:
        async with self.async_session_local() as db:
            return db

    def ping(self) -> None:
        with self.sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def before_cursor_execute(
        self,
        conn: Connection,
        cursor: CursorResult,
        statement: str,
        parameters: list[t.Any],
        context: ExecutionContext | None = None,
        executemany: bool = False,
    ):
        start_time = time.perf_counter()
        setattr(context, "start_time", start_time)

    def after_cursor_execute(
        self,
        conn: Connection,
        cursor: CursorResult,
        statement: str,
        parameters: list[t.Any],
        context: ExecutionContext | None = None,
        executemany: bool = False,
    ):
        queries = getattr(self.data, "queries", None) or []
        queries.append(
            RecordedQuery(
                statement=statement,
                parameters=parameters,
                end_time=time.perf_counter(),
                start_time=getattr(context, "start_time"),
            )
        )

        self.data.queries = queries

    def get_recorded_queries(self) -> list[RecordedQuery]:
        return getattr(self.data, "queries", None) or []  # type: ignore

    def create_async_engine(self, *, dsn: str, debug: bool = False) -> AsyncEngine:
        engine_options: dict[str, t.Any] = dict(echo=debug)
        return _create_async_engine(dsn, **engine_options)


__all__ = ["DatabaseEngine"]
