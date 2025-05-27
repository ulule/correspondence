from dataclasses import dataclass
from datetime import timedelta

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence import jwt
from correspondence.conf import settings
from correspondence.db import deps
from correspondence.models import AnonymousUser, User
from correspondence.utils import utc_now


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@dataclass
class AuthState:
    user: User | AnonymousUser
    reason: str = ""


def get_user_token(user: User) -> str:
    return jwt.encode(data={"user_id": user.id})


def authenticate(user: User, response: Response) -> str:
    token = get_user_token(user)

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        expires=utc_now() + timedelta(seconds=settings.SESSION_COOKIE_AGE),
    )

    return token


async def get_auth_state_from_cookie(cookie: str, asession: AsyncSession) -> AuthState:
    try:
        data = jwt.decode(token=cookie)
    except jwt.DecodeError:
        return AuthState(
            reason="unable to decode authentication token", user=AnonymousUser()
        )

    user_id = data.get("user_id")
    if not user_id:
        return AuthState(reason="user ID not found in token", user=AnonymousUser())

    user = await User.repository(asession).aget(user_id)
    if not user:
        return AuthState(
            reason=f"unable to find user with ID {user_id}", user=AnonymousUser()
        )

    return AuthState(user=user)


async def get_auth_state(
    request: Request, asession: AsyncSession = Depends(deps.get_db_asession)
) -> AuthState:
    cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie:
        return AuthState(reason="authentication cookie not found", user=AnonymousUser())

    return await get_auth_state_from_cookie(cookie, asession)


async def get_authenticated_user(
    state: AuthState = Depends(get_auth_state),
) -> User:
    if not state.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=state.reason)

    return state.user  # type:ignore


async def get_user(state: AuthState = Depends(get_auth_state)) -> User | AnonymousUser:
    return state.user


async def login(asession: AsyncSession, email: str, password: str) -> User:
    user = await User.repository(asession).aget_by(
        filter_by={"email": email, "is_staff": True}
    )
    errors = [
        {
            "type": "value_error",
            "loc": ("body", "email"),
            "msg": "A user does not exists either with this email or password",
            "input": email,
        },
        {
            "type": "value_error",
            "loc": ("body", "password"),
            "msg": "A user does not exists either with this email or password",
            "input": password,
        },
    ]
    if not user:
        raise RequestValidationError(errors)

    if not user.check_password(password):
        raise RequestValidationError(errors)

    return user
