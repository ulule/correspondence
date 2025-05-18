import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event

from correspondence.db.deps import get_db_asession, get_db_session
from correspondence.db.engine import AsyncSession, Session
from correspondence.main import app

@pytest.fixture()
def client(session: Session) -> Generator:
    app.dependency_overrides[get_db_session] = lambda: session

    yield TestClient(app)


@pytest_asyncio.fixture()
async def aclient(asession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield asession

    app.dependency_overrides[get_db_asession] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def asession(event_loop):
    async with app.db.async_engine.connect() as aconn:
        await aconn.begin()
        await aconn.begin_nested()
        async_session = AsyncSession(aconn, expire_on_commit=False)

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if aconn.closed:
                return

            if not aconn.in_nested_transaction():
                aconn.sync_connection.begin_nested()  # type: ignore

        yield


@pytest.fixture(scope="session")
def session() -> Generator:
    conn = app.db.sync_engine.connect()
    conn.begin()
    transaction = conn.begin_nested()
    session = Session(bind=conn)
    yield session
    session.close()
    transaction.rollback()
    conn.close()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
