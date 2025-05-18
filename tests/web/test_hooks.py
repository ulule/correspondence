import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence.models import MessagePart, Organization, PhoneNumber, User
from correspondence.test.client import AsyncClient

NEXMO_PAYLOAD_UNIQUE = {
    "msisdn": "33679368526",
    "to": "33644605843",
    "messageId": "0A0000000123ABCD5",
    "text": "Hello world",
    "type": "text",
    "keyword": "Hello",
    "message-timestamp": "2020-01-01T12:00:00.000+00:00",
    "timestamp": "1578787200",
    "nonce": "aaaaaaaa-bbbb-cccc-dddd-0123456789ab",
    "data": "abc123",
    "udh": "abc123",
}

NEXMO_PAYLOAD_MULTIPART = [
    {
        "msisdn": "33679368526",
        "to": "33644605843",
        "messageId": "0A0000000123ABCD2",
        "text": "Hello world",
        "type": "text",
        "keyword": "Hello",
        "message-timestamp": "2020-01-01T12:00:00.000+00:00",
        "timestamp": "1578787200",
        "nonce": "aaaaaaaa-bbbb-cccc-dddd-0123456789ab",
        "concat": "true",
        "concat-ref": "1",
        "concat-total": "3",
        "concat-part": "2",
        "data": "abc123",
        "udh": "abc123",
    },
    {
        "msisdn": "33679368526",
        "to": "33644605843",
        "messageId": "0A0000000123ABCD1",
        "text": "Hello my friend",
        "type": "text",
        "keyword": "Hello",
        "message-timestamp": "2020-01-01T12:00:00.000+00:00",
        "timestamp": "1578787200",
        "nonce": "aaaaaaaa-bbbb-cccc-dddd-0123456789ab",
        "concat": "true",
        "concat-ref": "1",
        "concat-total": "3",
        "concat-part": "1",
        "data": "abc123",
        "udh": "abc123",
    },
    {
        "msisdn": "33679368526",
        "to": "33644605843",
        "messageId": "0A0000000123ABCD3",
        "text": "Bye bye",
        "type": "text",
        "keyword": "Hello",
        "message-timestamp": "2020-01-01T12:00:00.000+00:00",
        "timestamp": "1578787200",
        "nonce": "aaaaaaaa-bbbb-cccc-dddd-0123456789ab",
        "concat": "true",
        "concat-ref": "1",
        "concat-total": "3",
        "concat-part": "3",
        "data": "abc123",
        "udh": "abc123",
    },
]


@pytest.mark.asyncio
async def test_hooks_nexmo_unique(
    aclient: AsyncClient,
    default_organization: Organization,
    default_phone_number: PhoneNumber,
    asession: AsyncSession,
):
    user = await User.repository(asession).acreate(
        first_name="Florent",
        last_name="Messa",
        phone_number="+33679368526",
        email="florent@ulule.com",
        organization=default_organization,
        organization_id=default_organization.id,
        country="FR",
    )

    payload = NEXMO_PAYLOAD_UNIQUE
    payload["to"] = default_phone_number.number

    response = await aclient.post(
        "/hooks/nexmo",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK

    conversation = await user.get_conversation(asession)
    assert conversation is not None
    assert conversation.messages_count == 1
    last_message = await conversation.get_last_message(asession)
    assert last_message is not None
    assert last_message.sender_id == user.id
    assert last_message.body == payload["text"]


@pytest.mark.asyncio
async def test_hooks_nexmo_multipart(
    aclient: AsyncClient,
    default_organization: Organization,
    default_phone_number: PhoneNumber,
    asession: AsyncSession,
):
    user = await User.repository(asession).acreate(
        first_name="Florent",
        last_name="Messa",
        phone_number="+33679368526",
        email="florent@ulule.com",
        organization=default_organization,
        organization_id=default_organization.id,
        country="FR",
    )

    for payload in NEXMO_PAYLOAD_MULTIPART:
        payload["to"] = default_phone_number.number

        response = await aclient.post(
            "/hooks/nexmo",
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK

    parts = await MessagePart.repository(asession).aall(
        filter_by={"part_ref": NEXMO_PAYLOAD_MULTIPART[0]["concat-ref"]}
    )
    assert len(parts) == len(NEXMO_PAYLOAD_MULTIPART)
    for part in parts:
        assert part.sender_id == user.id
        assert part.message_id is not None

    conversation = await user.get_conversation(asession)
    assert conversation is not None
    assert conversation.messages_count == 1
    last_message = await conversation.get_last_message(asession)
    assert last_message is not None
    assert last_message.sender_id == user.id
    assert last_message.body == "Hello my friendHello worldBye bye"
