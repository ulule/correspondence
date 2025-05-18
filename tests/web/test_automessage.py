from urllib.parse import parse_qs

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence.models import AutoMessage, User
from correspondence.test.client import AsyncClient

ACTIVE_CAMPAIGN_FORMDATA_COMPLETE = "contact%5Bid%5D=27760&contact%5Bemail%5D=gil.payet%40ulule.com&contact%5Bfirst_name%5D=Gil&contact%5Blast_name%5D=Payet&contact%5Bphone%5D=%2B33+6+78+36+85+26&contact%5Borgname%5D=Ulule&contact%5Bcustomer_acct_name%5D=Ulule&contact%5Btags%5D=Clicksend+Test&contact%5Bip4%5D=127.0.0.1&contact%5Bfields%5D%5Bgoogle_contacts-updated%5D=2019-06-28T08%3A12%3A35.769Z&contact%5Bfields%5D%5Bcontact_owner%5D=Alice+Pouillier&contact%5Bfields%5D%5Bgoogle_contacts-organization-name%5D=Ulule&contact%5Bfields%5D%5Bgoogle_contacts-organization-title%5D=CTO&contact%5Bfields%5D%5Bemail_lead_owner%5D=loic%40ulule.com&seriesid=929"

ACTIVE_CAMPAIGN_FORMDATA_PARTIAL = "contact%5Bid%5D=27760&contact%5Bphone%5D=%2B33+6+78+36+85+26&contact%5Borgname%5D=Ulule&contact%5Bcustomer_acct_name%5D=Ulule&contact%5Btags%5D=Clicksend+Test&contact%5Bip4%5D=127.0.0.1&contact%5Bfields%5D%5Bgoogle_contacts-updated%5D=2019-06-28T08%3A12%3A35.769Z&contact%5Bfields%5D%5Bcontact_owner%5D=Alice+Pouillier&contact%5Bfields%5D%5Bgoogle_contacts-organization-name%5D=Ulule&contact%5Bfields%5D%5Bgoogle_contacts-organization-title%5D=CTO&contact%5Bfields%5D%5Bemail_lead_owner%5D=loic%40ulule.com&seriesid=929"


@pytest.mark.asyncio
async def test_automessage_detail_with_partial_data(
    aclient: AsyncClient,
    staff_member: User,
    default_automessage: AutoMessage,
    asession: AsyncSession,
):
    url = f"/automessage/{default_automessage.id}"

    response = await aclient.post(
        url,
        data=ACTIVE_CAMPAIGN_FORMDATA_PARTIAL,
        headers={
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
    )

    data = parse_qs(ACTIVE_CAMPAIGN_FORMDATA_PARTIAL)

    assert response.status_code == status.HTTP_201_CREATED

    phone_number = data["contact[phone]"][0].replace(" ", "")

    user = await User.repository(asession).aget_by(
        filter_by={"phone_number": phone_number}
    )
    assert user is not None
    assert user.manager_id == staff_member.id
    assert user.first_name is None
    assert user.last_name is None
    assert user.email is None
    assert user.country is not None
    assert user.country == "FR"

    conversation = await user.get_conversation(asession)
    assert conversation is not None
    assert conversation.messages_count == 1

    last_message = await conversation.get_last_message(asession)
    assert last_message is not None
    assert last_message.automessage_id == default_automessage.id
    assert last_message.automessage_id == default_automessage.id
    assert last_message.sender_id == default_automessage.sender_id
    assert last_message.body == default_automessage.body


@pytest.mark.asyncio
async def test_automessage_detail_without_user(
    aclient: AsyncClient,
    staff_member: User,
    default_automessage: AutoMessage,
    asession: AsyncSession,
):
    url = f"/automessage/{default_automessage.id}"
    response = await aclient.post(
        url,
        data=ACTIVE_CAMPAIGN_FORMDATA_COMPLETE,
        headers={
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
    )

    data = parse_qs(ACTIVE_CAMPAIGN_FORMDATA_COMPLETE)

    assert response.status_code == status.HTTP_201_CREATED

    phone_number = data["contact[phone]"][0].replace(" ", "")

    user = await User.repository(asession).aget_by(
        filter_by={"phone_number": phone_number}
    )
    assert user is not None
    assert user.manager_id == staff_member.id
    assert user.active_campaign_id == data["contact[id]"][0]
    assert user.first_name == data["contact[first_name]"][0]
    assert user.last_name == data["contact[last_name]"][0]
    assert user.email == data["contact[email]"][0]

    conversation = await user.get_conversation(asession)
    assert conversation is not None
    assert conversation.messages_count == 1

    last_message = await conversation.get_last_message(asession)
    assert last_message is not None
    assert last_message.automessage_id == default_automessage.id
    assert last_message.sender_id == default_automessage.sender_id
    assert last_message.body == default_automessage.body

    response = await aclient.post(
        url,
        data=ACTIVE_CAMPAIGN_FORMDATA_COMPLETE,
        headers={
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
    )
    assert response.status_code == status.HTTP_200_OK
