from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel
from typing_extensions import Optional

from correspondence import models


class Resource(BaseModel):
    pass


class UserResource(Resource):
    id: int
    email: str | None = None
    name: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    created_at: datetime
    updated_at: datetime
    active_campaign_id: str | None = None
    messages_received_count: int = 0
    messages_sent_count: int = 0
    phone_number: str | None = None
    manager_id: int | None = None
    manager: "Optional[UserResource]" = None
    country: str | None = None

    @classmethod
    def from_model(
        cls, user: models.User, extra_fields: list[str] | None = None
    ) -> Self:
        resource = cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            messages_received_count=user.messages_received_count,
            messages_sent_count=user.messages_sent_count,
            active_campaign_id=user.active_campaign_id,
            country=user.country.code if user.country else None,
            phone_number=user.phone_number,
            manager_id=user.manager_id,
        )

        if extra_fields and "manager" in extra_fields:
            if user.manager_id and user.manager:
                resource.manager = cls.from_model(user.manager)

        return resource


class OrganizationResource(Resource):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    slug: str
    urls: dict[str, Any]
    supported_countries: list[str]

    @classmethod
    def from_model(cls, organization: models.Organization) -> Self:
        supported_countries = list(organization.supported_countries.keys())

        return cls(
            id=organization.id,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
            name=organization.name,
            slug=organization.slug,
            urls=organization.urls,
            supported_countries=supported_countries,
        )


class ConversationResource(Resource):
    id: int
    created_at: datetime
    updated_at: datetime
    messages_count: int
    unread: bool
    receiver: UserResource | None = None
    last_message: "Optional[MessageResource]" = None

    @classmethod
    def from_model(
        cls, conversation: models.Conversation, extra_fields: list[str] | None = None
    ) -> Self:
        resource = cls(
            id=conversation.id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            unread=conversation.unread,
            messages_count=conversation.messages_count,
        )

        if not extra_fields:
            return resource

        if "receiver" in extra_fields:
            if conversation.receiver_id and conversation.receiver:
                resource.receiver = UserResource.from_model(
                    conversation.receiver,
                    extra_fields=trim_prefix("receiver.", extra_fields),
                )

        if "last_message" in extra_fields:
            if conversation.last_message_id and conversation.last_message:
                resource.last_message = MessageResource.from_model(
                    conversation.last_message,
                    extra_fields=trim_prefix("last_message.", extra_fields),
                )

        return resource


class MessageResource(Resource):
    id: int
    created_at: datetime
    updated_at: datetime
    body: str
    conversation: ConversationResource | None = None
    sender: UserResource

    @classmethod
    def from_model(
        cls, message: models.Message, extra_fields: list[str] | None = None
    ) -> Self:
        resource = cls(
            id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            body=message.body,
            sender=UserResource.from_model(
                message.sender, extra_fields=trim_prefix("sender.", extra_fields)
            ),
        )

        if not extra_fields:
            return resource

        if "conversation" in extra_fields:
            if message.conversation_id and message.conversation:
                resource.conversation = ConversationResource.from_model(
                    message.conversation,
                    extra_fields=trim_prefix("conversation.", extra_fields),
                )

        return resource


def trim_prefix(prefix: str, extra_fields: list[str] | None = None) -> list[str] | None:
    if extra_fields is None:
        return None

    return [
        extra_field[len(prefix) :]
        for extra_field in extra_fields
        if prefix in extra_field
    ]
