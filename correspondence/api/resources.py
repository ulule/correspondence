import typing as t
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from typing_extensions import Optional

from correspondence.db.models import Model


class Schema(BaseModel):
    @classmethod
    def from_model(cls, model: Model) -> t.Self:  # type: ignore
        params: dict[str, t.Any] = {}
        for k, v in cls.__signature__.parameters.items():
            model_value = getattr(model, k)
            if v.annotation is type(model_value):
                params[k] = model_value
            elif v.annotation is str and isinstance(model_value, Enum):
                params[k] = model_value.name.lower()

        instance = cls(**params)

        return instance


class User(Schema):
    id: int
    email: str
    last_name: str
    first_name: str
    created_at: datetime
    country: str
    active_campaign_id: str
    messages_received_count: int
    messages_sent_count: int
    phone_number: str
    manager: "Optional[User]" = None


class Conversation(Schema):
    id: int
    created_at: datetime
    messages_count: int
    unread: bool
    receiver: User
