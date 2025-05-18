import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence.models import Organization, PhoneNumber, User


@pytest.mark.asyncio
async def test_transaction(
    asession: AsyncSession,
):
    async with asession.begin_nested():
        user = await User.repository(asession).acreate(
            first_name="Laura",
            last_name="Bocquillon",
            phone_number="+33700000000",
            email="laura@ulule.com",
            country="FR",
            is_staff=True,
            commit=False,
        )
        await asession.flush()
        assert user.id is not None

        user = await User.repository(asession).acreate(
            first_name="Florent",
            last_name="Messa",
            phone_number="+33600000000",
            email="florent@ulule.com",
            country="FR",
            is_staff=True,
            commit=False,
        )
        await asession.flush()
        assert user.id is not None


@pytest.mark.asyncio
async def test_models(
    asession: AsyncSession,
):
    user = await User.repository(asession).acreate(
        first_name="Laura",
        last_name="Bocquillon",
        phone_number="+33700000000",
        email="laura@ulule.com",
        country="FR",
        is_staff=True,
    )
    assert user.id is not None
    await User.repository(asession).abulk_update(
        filter_by={"id": user.id}, first_name="Florent", last_name="Messa"
    )
    updated_user = await User.repository(asession).aget(user.id)
    assert updated_user is not None
    assert updated_user.first_name == "Florent"
    assert updated_user.last_name == "Messa"

    user = await user.asave(
        asession,
        last_name="Bocquillon",
    )
    updated_user = await User.repository(asession).aget(user.id)
    assert updated_user is not None

    pk = updated_user.id
    assert updated_user.first_name == "Florent"
    assert updated_user.last_name == "Bocquillon"
    await updated_user.aupdate(asession, first_name="Laura")
    assert updated_user.first_name == "Laura"
    await updated_user.adelete(asession)
    updated_user = await User.repository(asession).aget(pk)
    assert updated_user is None
    await User.repository(asession).abulk_delete(filter_by={"id": pk})

    user, created = await User.repository(asession).aget_or_create(
        defaults={"first_name": "Florent", "last_name": "Messa", "country": "FR"},
        email="florent@ulule.com",
        phone_number="+33700000000",
    )
    assert user is not None
    assert created is True

    exists = await User.repository(asession).aexists(
        clauses=[User.email == "florent@ulule.com"]
    )
    assert exists is True

    count = await User.repository(asession).acount()
    assert count == 1

    count = await User.repository(asession).acount(
        filter_by={"email": "florent@ulule.com"}
    )
    assert count == 1


@pytest.mark.asyncio
async def test_organization_supported_countries(
    asession: AsyncSession,
    default_organization: Organization,
    default_phone_number: PhoneNumber,
):
    supported_countries = await Organization.get_supported_countries(
        asession, default_organization.id
    )
    assert len(supported_countries) != 0
    assert len(supported_countries[default_phone_number.country.code]) == 1
    assert (
        supported_countries[default_phone_number.country.code][0]
        == default_phone_number
    )


@pytest.mark.asyncio
async def test_organization_get_from_phone_number(
    asession: AsyncSession,
    default_phone_number: PhoneNumber,
):
    org = await Organization.get_from_phone_number(
        asession, default_phone_number.number
    )
    assert org is not None
    assert org.id == default_phone_number.organization_id
