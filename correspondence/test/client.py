from typing import Any

from httpx import URL
from httpx import AsyncClient as BaseAsyncClient
from httpx import Response

from correspondence import auth
from correspondence.conf import settings
from correspondence.models import User


class AsyncClient(BaseAsyncClient):
    async def post(
        self, url: URL | str, user: User | None = None, **kwargs: Any
    ) -> Response:
        if user:
            token = auth.get_user_token(user)
            kwargs["cookies"] = {settings.SESSION_COOKIE_NAME: token}

        return await super().post(url, **kwargs)

    async def patch(
        self, url: URL | str, user: User | None = None, **kwargs: Any
    ) -> Response:
        if user:
            token = auth.get_user_token(user)
            kwargs["cookies"] = {settings.SESSION_COOKIE_NAME: token}

        return await super().patch(url, **kwargs)

    async def get(
        self, url: URL | str, user: User | None = None, **kwargs: Any
    ) -> Response:
        if user:
            token = auth.get_user_token(user)
            kwargs["cookies"] = {settings.SESSION_COOKIE_NAME: token}

        return await super().get(url, **kwargs)
