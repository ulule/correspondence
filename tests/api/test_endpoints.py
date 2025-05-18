import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence.models import Conversation, Message, Organization, User
from correspondence.test.client import AsyncClient


@pytest.mark.asyncio
async def test_user_conversation_detail_empty(
    aclient: AsyncClient, default_user: User, staff_member: User
):
    url = f"/api/users/{default_user.id}/conversation/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == 0


@pytest.mark.asyncio
async def test_user_conversation_detail(
    aclient: AsyncClient,
    default_user: User,
    staff_member: User,
    default_conversation: Conversation,
    asession: AsyncSession,
):
    url = f"/api/users/{default_user.id}/conversation/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == default_conversation.id
    assert body["receiver"] is not None

    message = await default_user.create_message(
        asession, send=False, body="Hello world!"
    )
    assert message is not None

    conversation = await default_conversation.refresh_from_db(asession)
    assert conversation is not None
    assert conversation.last_message_id is not None
    assert conversation.messages_count == 1

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == default_conversation.id
    assert body["receiver"] is not None
    assert body["last_message"] is not None
    assert body["last_message"]["id"] == message.id
    assert body["last_message"]["sender"] is not None
    assert body["last_message"]["sender"]["id"] == default_user.id
    assert body["last_message"]["conversation"] is None


@pytest.mark.asyncio
async def test_conversation_message_list(
    aclient: AsyncClient,
    default_conversation: Conversation,
    asession: AsyncSession,
    staff_member: User,
):
    url = f"/api/conversations/{default_conversation.id}/messages/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK

    message = await default_conversation.receiver.create_message(
        asession, sender=staff_member, send=False, body="Hello world!"
    )
    assert message is not None
    conversation = await default_conversation.refresh_from_db(asession)
    assert conversation is not None
    assert conversation.last_message_id is not None
    assert conversation.messages_count == 1

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == message.id
    assert body["data"][0]["sender"] is not None
    assert body["data"][0]["sender"]["id"] == staff_member.id
    assert body["data"][0]["conversation"] is not None
    assert body["data"][0]["conversation"]["id"] == default_conversation.id
    assert body["data"][0]["conversation"]["receiver"] is not None
    assert (
        body["data"][0]["conversation"]["receiver"]["id"]
        == default_conversation.receiver_id
    )


@pytest.mark.asyncio
async def test_user_list(
    aclient: AsyncClient, asession: AsyncSession, staff_member: User
):
    url = "/api/users/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["data"]) == 1

    user = await User.repository(asession).acreate(
        first_name="Laura",
        last_name="Bocquillon",
        phone_number="+33700000001",
        email="laura.bocquillon@ulule.com",
        country="FR",
    )

    response = await aclient.get(url, user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["id"] == user.id

    staff_member = await User.repository(asession).acreate(
        first_name="Florent",
        last_name="Message",
        phone_number="+33600000001",
        email="florent.messa@ulule.com",
        country="FR",
        is_staff=True,
    )

    response = await aclient.get(f"{url}?is_staff=1", user=staff_member)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["id"] == staff_member.id


@pytest.mark.asyncio
async def test_user_update(
    aclient: AsyncClient,
    default_user: User,
    staff_member: User,
    asession: AsyncSession,
):
    url = f"/api/users/{default_user.id}/"
    response = await aclient.patch(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.patch(
        url,
        json={
            "first_name": "Florent",
            "last_name": "Messa",
            "country": "FR",
        },
        user=staff_member,
    )

    assert response.status_code == status.HTTP_200_OK

    response = await aclient.patch(
        url,
        json={"first_name": "Laura", "phone_number": "+33600000000"},
        user=staff_member,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    user = await User.repository(asession).aget(body["id"])
    assert user is not None
    assert user.first_name == "Laura"
    assert user.last_name == "Messa"
    assert user.country == "FR"
    assert user.phone_number == "+33600000000"

    response = await aclient.patch(
        url,
        json={
            "manager_id": staff_member.id,
        },
        user=staff_member,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    user = await User.repository(asession).aget(body["id"])
    assert user is not None
    assert user.manager_id == staff_member.id


@pytest.mark.asyncio
async def test_user_create(
    aclient: AsyncClient,
    staff_member: User,
    asession: AsyncSession,
    default_organization: Organization,
):
    url = f"/api/organizations/{default_organization.slug}/users/"
    response = await aclient.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.post(url, json={}, user=staff_member)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    payload = {
        "phone_number": "+33679368526",
        "country": "FR",
        "manager_id": staff_member.id,
    }

    response = await aclient.post(
        url,
        json=payload,
        user=staff_member,
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()

    user = await User.repository(asession).aget(body["id"])
    assert user is not None
    assert user.phone_number == payload["phone_number"]
    assert user.country == payload["country"]
    assert user.manager_id == payload["manager_id"]
    assert user.organization_id == default_organization.id


@pytest.mark.asyncio
async def test_user_conversation_create(
    aclient: AsyncClient,
    staff_member: User,
    default_user: User,
    asession: AsyncSession,
):
    conversation = await Conversation.repository(asession).aget_by(
        filter_by={"receiver_id": default_user.id}
    )
    assert conversation is None

    url = f"/api/users/{default_user.id}/conversation/"
    payload = {
        "body": "A new message in the conversation",
    }

    response = await aclient.post(url, json={})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.post(
        url,
        json=payload,
        user=staff_member,
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body.get("id") is not None

    conversation = await Conversation.repository(asession).aget_by(
        filter_by={"receiver_id": default_user.id}
    )
    assert conversation is not None

    message = await Message.repository(asession).aget(body["id"])
    assert message is not None
    assert message.sender_id == staff_member.id
    assert message.body == payload["body"]
    assert message.conversation_id == conversation.id
    assert conversation.messages_count == 1
    assert conversation.last_message_id == message.id
    assert conversation.unread is False

    new_payload = {
        "sender_id": default_user.id,
        "body": "A new reply which has to be unread",
    }

    response = await aclient.post(
        url,
        json=new_payload,
        user=staff_member,
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body.get("id") is not None
    message = await Message.repository(asession).aget(body["id"])
    assert message is not None

    conversation = await conversation.refresh_from_db(asession)
    assert conversation is not None
    assert conversation.messages_count == 2
    assert conversation.last_message_id == message.id
    assert conversation.last_message.body == new_payload["body"]
    assert conversation.unread is True


@pytest.mark.asyncio
async def test_organization_conversation_list(
    aclient: AsyncClient, default_organization: Organization, staff_member: User
):
    url = f"/api/organizations/{default_organization.slug}/conversations/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(
        url,
        user=staff_member,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_conversation_action(
    aclient: AsyncClient,
    default_conversation: Conversation,
    asession: AsyncSession,
    staff_member: User,
):
    response = await aclient.post(
        f"/api/conversations/{default_conversation.id}/foo/", user=staff_member
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await aclient.post(f"/api/conversations/{default_conversation.id}/read/")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.post(
        f"/api/conversations/{default_conversation.id}/read/", user=staff_member
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["unread"] is False
    conversation = await default_conversation.refresh_from_db(asession)
    assert conversation is not None
    assert conversation.unread is False

    response = await aclient.post(
        f"/api/conversations/{default_conversation.id}/unread/",
        user=staff_member,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["unread"] is True
    conversation = await default_conversation.refresh_from_db(asession)
    assert conversation is not None
    assert conversation.unread is True
