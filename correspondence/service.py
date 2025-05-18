from enum import Enum
from typing import Any

import phonenumbers
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession

from correspondence.api import payloads
from correspondence.conf import settings
from correspondence.models import Conversation, Message, Organization, User
from correspondence.provider import Provider


class UserService:
    async def update(
        self,
        asession: AsyncSession,
        user: User,
        payload: payloads.UserUpdatePayload,
    ) -> User:
        data = payload.model_dump(exclude_unset=True)
        repo = User.repository(asession)

        errors: list[Any] = []
        for field_name in ("phone_number", "active_campaign_id", "email"):
            if value := data.get(field_name):
                exists = await repo.aexists(
                    clauses=[getattr(User, field_name) == value, User.id != user.id]
                )
                if exists:
                    errors.append(
                        {
                            "type": "value_error",
                            "loc": ("body", field_name),
                            "msg": "A user with this value already exists.",
                            "input": value,
                        }
                    )
                setattr(user, field_name, value)

        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]

        if "email" in data:
            user.email = data["email"]

        if phone_number := data.get("phone_number"):
            country_code = settings.DEFAULT_COUNTRY
            if user.country:
                country_code = user.country.code

            phone_number_instance = phonenumbers.parse(
                phone_number,
                country_code,
            )

            user.phone_number = f"+{phone_number_instance.country_code}{phone_number_instance.national_number}"

        if country := data.get("country"):
            user.country = country

        if manager_id := data.get("manager_id"):
            manager = await User.repository(asession).aget_by(
                filter_by={
                    "id": manager_id,
                    "is_staff": True,
                }
            )
            if not manager:
                errors.append(
                    {
                        "type": "value_error",
                        "loc": ("body", "manager_id"),
                        "msg": "A manager with this ID doesn't exist",
                        "input": payload.manager_id,
                    }
                )
            else:
                user.manager = manager
                user.manager_id = manager.id

        if len(errors):
            raise RequestValidationError(errors)

        return await user.asave(asession)

    async def create(
        self,
        asession: AsyncSession,
        organization: Organization,
        payload: payloads.UserCreatePayload,
    ) -> User:
        phone_number_instance = phonenumbers.parse(
            payload.phone_number,
            payload.country,
        )

        phone_number = f"+{phone_number_instance.country_code}{phone_number_instance.national_number}"
        errors: list[Any] = []
        if await User.repository(asession).aexists(
            clauses=[User.phone_number == phone_number]
        ):
            errors.append(
                {
                    "type": "value_error",
                    "loc": ("body", "phone_number"),
                    "msg": "A user with this phone_number already exists.",
                    "input": phone_number,
                }
            )

        if (email := payload.email) and await User.repository(asession).aexists(
            clauses=[User.email == email]
        ):
            errors.append(
                {
                    "type": "value_error",
                    "loc": ("body", "email"),
                    "msg": "A user with this email already exists.",
                    "input": payload.email,
                }
            )

        manager = await User.repository(asession).aget_by(
            filter_by={
                "id": payload.manager_id,
                "is_staff": True,
            }
        )
        if not manager:
            errors.append(
                {
                    "type": "value_error",
                    "loc": ("body", "manager_id"),
                    "msg": "A manager with this ID doesn't exist",
                    "input": payload.manager_id,
                }
            )

        if len(errors):
            raise RequestValidationError(errors)

        return await User.repository(asession).acreate(
            phone_number=phone_number,
            manager=manager,
            manager_id=manager.id,  # type: ignore
            country=payload.country,
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            active_campaign_id=payload.active_campaign_id,
            organization=organization,
            organization_id=organization.id,
        )

    async def create_message(
        self,
        asession: AsyncSession,
        provider: Provider,
        sender: User,
        receiver: User,
        payload: payloads.MessageCreatePayload,
    ) -> Message:
        return await receiver.create_message(
            asession,
            payload.body,
            sender=sender,
        )


class ConversationAction(str, Enum):
    read = "read"
    unread = "unread"


class ConversationService:
    async def mark_as(
        self,
        asession: AsyncSession,
        conversation: Conversation,
        action: ConversationAction,
    ) -> Conversation:
        match action:
            case ConversationAction.read:
                await conversation.aupdate(asession, unread=False)
            case ConversationAction.unread:
                await conversation.aupdate(asession, unread=True)
        return conversation


user_service = UserService()
conversation_service = ConversationService()

__all__ = [
    "ConversationAction",
    "user_service",
    "conversation_service",
]
