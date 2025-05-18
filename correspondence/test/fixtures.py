from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport
from sqlalchemy import event

from correspondence.db.deps import get_db_asession, get_db_session
from correspondence.db.engine import AsyncSession, Session
from correspondence.main import app
from correspondence.models import (AutoMessage, Conversation, Organization,
                                   PhoneNumber, User)

from .client import AsyncClient

DEFAULT_PASSWORD = "$ecret"


@pytest_asyncio.fixture()
async def staff_member(asession: AsyncSession):
    user = User(
        first_name="Laura",
        last_name="Bocquillon",
        phone_number="+33700000000",
        email="laura@ulule.com",
        country="FR",
        is_staff=True,
    )
    user.set_password(DEFAULT_PASSWORD)
    await user.asave(asession)

    return user


@pytest_asyncio.fixture()
async def default_phone_number(
    asession: AsyncSession, default_organization: Organization
):
    return await PhoneNumber.repository(asession).acreate(
        number="+33600000000",
        country="FR",
        organization_id=default_organization.id,
    )


@pytest_asyncio.fixture()
async def default_message(asession: AsyncSession, default_user: User):
    return await default_user.create_message(asession, send=False, body="Hello world!")


@pytest_asyncio.fixture()
async def default_automessage(
    asession: AsyncSession, staff_member: User, default_organization: Organization
):
    return await AutoMessage.repository(asession).acreate(
        body="Coucou, c'est un message initial!",
        sender_id=staff_member.id,
        organization_id=default_organization.id,
    )


@pytest_asyncio.fixture()
async def default_organization(asession: AsyncSession, staff_member: User):
    return await Organization.repository(asession).acreate(
        name="Ulule",
        slug="ulule",
        owner_id=staff_member.id,
        owner=staff_member,
        country="FR",
    )


@pytest_asyncio.fixture()
async def default_user(
    asession: AsyncSession, default_organization: Organization
) -> User:
    return await User.repository(asession).acreate(
        email="florent@ulule.com",
        country="FR",
        organization_id=default_organization.id,
    )


@pytest_asyncio.fixture()
async def default_conversation(
    asession: AsyncSession, default_user: User, default_organization: Organization
) -> Conversation:
    return await Conversation.repository(asession).acreate(
        receiver_id=default_user.id, organization_id=default_organization.id
    )


@pytest.fixture()
def client(session: Session) -> Generator:
    app.dependency_overrides[get_db_session] = lambda: session

    yield TestClient(app)


@pytest_asyncio.fixture()
async def aclient(asession: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield asession

    app.dependency_overrides[get_db_asession] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def asession():
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

        yield async_session


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
