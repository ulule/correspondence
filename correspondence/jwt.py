from datetime import datetime, timedelta
from typing import Any

import jwt

from .conf import settings
from .utils import utc_now

ALGORITHM = "HS256"

DecodeError = jwt.DecodeError
ExpiredSignatureError = jwt.ExpiredSignatureError


def create_expiration_dt(seconds: int) -> datetime:
    return utc_now() + timedelta(seconds=seconds)


def encode(
    *,
    data: dict[str, Any],
    secret: str | None = None,
    expires_at: datetime | None = None,
    expires_in: int | None = None,
) -> str:
    to_encode = data.copy()
    secret = secret or settings.SECRET
    if not expires_at:
        expires_in = expires_in or settings.SESSION_COOKIE_AGE
        expires_at = create_expiration_dt(seconds=expires_in)

    to_encode["exp"] = expires_at
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def decode(
    token: str,
) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
