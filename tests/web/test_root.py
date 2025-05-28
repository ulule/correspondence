import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence import auth, jwt
from correspondence.conf import settings
from correspondence.models import Organization, User
from correspondence.test.client import AsyncClient
from correspondence.test.fixtures import DEFAULT_PASSWORD


@pytest.mark.asyncio
async def test_healthcheck(aclient: AsyncClient):
    response = await aclient.get("/healthcheck")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body.get("message") == "ok"


@pytest.mark.asyncio
async def test_login(aclient: AsyncClient, staff_member: User):
    response = await aclient.post(
        "/login", json={"email": staff_member.email, "password": "foo"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await aclient.post(
        "/login", json={"email": staff_member.email, "password": DEFAULT_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK
    cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
    assert cookie is not None
    data = jwt.decode(token=cookie)
    assert data.get("user_id") == staff_member.id

    response = await aclient.get(
        "/admin",
        cookies=response.cookies,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_admin(aclient: AsyncClient, staff_member: User):
    response = await aclient.get(
        "/admin",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(
        "/admin", cookies={settings.SESSION_COOKIE_NAME: "foo"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["detail"] == "unable to decode authentication token"

    response = await aclient.get(
        "/admin",
        cookies={
            settings.SESSION_COOKIE_NAME: jwt.encode(
                data={"user_id": 100},
            )
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["detail"] == "unable to find user with ID 100"

    response = await aclient.get(
        "/admin",
        cookies={
            settings.SESSION_COOKIE_NAME: jwt.encode(
                data={"user_id": 100}, secret="foo"
            )
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["detail"] == "unable to decode authentication token"

    response = await aclient.get(
        "/admin",
        user=staff_member,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_root(
    aclient: AsyncClient, default_organization: Organization, default_user: User
):
    response = await aclient.get(
        "/",
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == f"{aclient.base_url}/signin"

    response = await aclient.get(
        "/",
        user=default_organization.owner,
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert (
        response.headers["location"]
        == f"{aclient.base_url}/organizations/{default_organization.slug}/"
    )

    response = await aclient.get(
        "/",
        user=default_user,
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert (
        response.headers["location"]
        == f"{aclient.base_url}/organizations/{default_organization.slug}/"
    )


@pytest.mark.asyncio
async def test_organization_detail(
    aclient: AsyncClient, default_organization: Organization, default_user: User
):
    url = f"/organizations/{default_organization.slug}/"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await aclient.get(
        url,
        user=default_organization.owner,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_signin(
    aclient: AsyncClient,
    default_organization: Organization,
    staff_member: User,
    asession: AsyncSession,
):
    url = "/signin"
    response = await aclient.get(url)
    assert response.status_code == status.HTTP_200_OK

    url = "/signin"
    response = await aclient.post(
        url, data={"email": staff_member.email, "password": DEFAULT_PASSWORD}
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == f"{aclient.base_url}/"
    assert settings.SESSION_COOKIE_NAME in response.cookies
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]

    auth_state = await auth.get_auth_state_from_cookie(cookie, asession)
    assert auth_state.user.is_authenticated is True
    assert auth_state.user == staff_member


@pytest.mark.asyncio
async def test_logout(
    aclient: AsyncClient,
    staff_member: User,
):
    url = "/logout"
    response = await aclient.get(
        url, cookies={settings.SESSION_COOKIE_NAME: auth.get_user_token(staff_member)}
    )

    assert settings.SESSION_COOKIE_NAME not in response.cookies
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == f"{aclient.base_url}/"
