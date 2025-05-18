import asyncio
import random
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional, Self

import bcrypt
from sqlalchemy import (INTEGER, TIMESTAMP, Boolean, ForeignKey, Integer,
                        String, Text, event)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (Mapped, Session, joinedload, mapped_column,
                            relationship, selectinload)
from sqlalchemy_utils import Country, CountryType

from correspondence.db.models import Model
from correspondence.db.sql import select
from correspondence.pagination import QueryPaginationParams, paginate
from correspondence.provider import Provider


class User(Model):
    __abstract__ = False
    __tablename__ = "correspondence_user"

    id: Mapped[int] = mapped_column(
        INTEGER,
        primary_key=True,
    )
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active_campaign_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_staff: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default="False"
    )
    is_superuser: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default="False"
    )
    messages_sent_count: Mapped[int] = mapped_column(
        Integer, nullable=True, server_default="0"
    )
    messages_received_count: Mapped[int] = mapped_column(
        Integer, nullable=True, server_default="0"
    )
    manager_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=True,
    )
    manager: Mapped["Optional[User]"] = relationship(
        remote_side=[id], viewonly=True, lazy="raise"
    )
    country: Mapped[Country | None] = mapped_column(CountryType, nullable=True)

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped["Optional[Organization]"] = relationship(
        foreign_keys=[organization_id], viewonly=True, lazy="raise"
    )

    @property
    def name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        if self.first_name:
            return self.first_name

        if self.last_name:
            return self.last_name

        return "Anonymous"

    async def get_conversation(
        self, asession: AsyncSession
    ) -> "Optional[Conversation]":
        query = (
            select(Conversation)
            .where(Conversation.receiver_id == self.id)
            .options(
                joinedload(Conversation.phone_number),
                joinedload(Conversation.last_message).selectinload(Message.sender),
                joinedload(Conversation.receiver, innerjoin=True),
            )
        )
        res = await asession.scalars(query)
        conversation = res.unique().one_or_none()
        if conversation is None:
            return conversation

        if conversation.receiver:
            conversation.receiver.manager = self.manager

        return conversation

    async def has_automessage(
        self, asession: AsyncSession, automessage: "AutoMessage"
    ) -> bool:
        conversation = await self.get_conversation(asession)
        if not conversation:
            return False

        return await conversation.has_automessage(asession, automessage)

    async def get_or_create_conversation(
        self, asession: AsyncSession, commit: bool = True
    ) -> tuple["Conversation", bool]:
        conversation = await self.get_conversation(asession)
        created = False
        if not conversation:
            conversation = Conversation(
                receiver=self,
                receiver_id=self.id,
                organization_id=self.organization_id,
            )

            if self.country and self.organization_id:
                phone_numbers = await Organization.get_supported_countries(
                    asession, self.organization_id
                )

                if phone_numbers and (choices := phone_numbers.get(self.country.code)):
                    phone_number = random.choices(choices)[0]

                    conversation.phone_number = phone_number
                    conversation.phone_number_id = phone_number.id

            await conversation.asave(asession)

            created = True

        return conversation, created

    async def create_message(
        self,
        asession: AsyncSession,
        body: str,
        send: bool = True,
        sender: "Optional[User]" = None,
        manager: "Optional[User]" = None,
        extra_data: dict[str, Any] | None = None,
    ) -> "Message":
        async with asession.begin_nested():
            conversation, _ = await self.get_or_create_conversation(asession)

            sender = sender or self

            message = await conversation.create_message(
                asession,
                sender,
                body,
                send=send,
                extra_data=extra_data,
            )

            return message

    @classmethod
    async def paginate(
        cls,
        asession: AsyncSession,
        pagination: QueryPaginationParams,
    ) -> tuple[list["User"], int]:
        query = select(User).order_by(User.created_at.desc(), User.id.desc())
        if pagination.is_staff:
            query = query.filter(User.is_staff.is_(True))

        return await paginate(asession, User.id, query, pagination)

    def set_password(self, password: str):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        self.password = hashed.decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password:
            return False

        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    async def get_default_organization(
        self, asession: AsyncSession
    ) -> "Optional[Organization]":
        org = await Organization.repository(asession).aget_by(
            filter_by={"owner_id": self.id}
        )

        if org:
            return org

        return await Organization.repository(asession).aget(self.organization_id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class AnonymousUser:
    id = None
    pk = None
    username = ""
    is_staff = False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def __str__(self):
        return "AnonymousUser"


class PhoneNumber(Model):
    __abstract__ = False
    __tablename__ = "correspondence_phone_number"

    number: Mapped[str] = mapped_column(String(255))
    country: Mapped[Country] = mapped_column(CountryType)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=False,
    )

    organization: Mapped["Optional[Organization]"] = relationship(
        foreign_keys=[organization_id],
        viewonly=True,
        lazy="raise",
    )


class MessagePart(Model):
    __abstract__ = False
    __tablename__ = "correspondence_messagepart"

    provider_id: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text)
    part_id: Mapped[int] = mapped_column(Integer)
    part_ref: Mapped[str] = mapped_column(String(100))

    message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_message.id"),
        nullable=True,
    )

    message: Mapped["Optional[Message]"] = relationship(
        foreign_keys=[message_id], viewonly=True, lazy="raise"
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )
    sender: Mapped[User] = relationship(
        foreign_keys=[sender_id], viewonly=True, lazy="raise"
    )

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped["Optional[Organization]"] = relationship(
        foreign_keys=[organization_id],
        viewonly=True,
        lazy="raise",
    )


class AutoMessage(Model):
    __abstract__ = False
    __tablename__ = "correspondence_automessage"

    body: Mapped[str] = mapped_column(Text())

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )
    sender: Mapped[User] = relationship(
        foreign_keys=[sender_id], viewonly=True, lazy="raise"
    )

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped["Optional[Organization]"] = relationship(
        foreign_keys=[organization_id],
        viewonly=True,
        lazy="raise",
    )

    async def send_message(
        self,
        asession: AsyncSession,
        provider: Provider,
        phone_number: str,
        defaults: dict[str, Any] | None = None,
    ) -> "Optional[Message]":
        defaults = defaults or {}
        user = await User.repository(asession).aget_by(
            filter_by={"phone_number": phone_number}, options=[joinedload(User.manager)]
        )
        async with asession.begin_nested():
            if not user:
                user = User(
                    phone_number=phone_number,
                    manager=self.sender,
                    manager_id=self.sender.id,
                    organization_id=self.organization_id,
                    **defaults,
                )

                await user.asave(asession)

            if await user.has_automessage(asession, self):
                return None

            await asession.flush()

            message = await user.create_message(
                asession,
                self.body,
                sender=self.sender,
                manager=self.sender,
                extra_data={"automessage_id": self.id},
            )

            return message


class Message(Model):
    __abstract__ = False
    __tablename__ = "correspondence_message"

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )
    sender: Mapped[User] = relationship(
        foreign_keys=[sender_id], viewonly=True, lazy="raise"
    )

    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_conversation.id"),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", foreign_keys=[conversation_id], viewonly=True, lazy="raise"
    )

    automessage_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_automessage.id"),
        nullable=True,
    )

    automessage: Mapped["AutoMessage"] = relationship(
        "AutoMessage", foreign_keys=[automessage_id], viewonly=True, lazy="raise"
    )

    body: Mapped[str] = mapped_column(Text())

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped["Optional[Organization]"] = relationship(
        foreign_keys=[organization_id], viewonly=True, lazy="raise"
    )

    provider_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    provider_ids: Mapped[list[str]] = mapped_column(ARRAY(String(255)), nullable=True)

    async def async_send(self):
        from correspondence.broker import message_sent

        await message_sent.kiq(self.id)

    async def send(
        self,
        asession: AsyncSession,
        provider: Provider,
        commit: bool = True,
    ) -> None:
        receiver = self.conversation.receiver

        from_ph = None
        if (
            not self.conversation.phone_number_id
            or not self.conversation.phone_number.is_active
        ):
            supported_countries = await Organization.get_supported_countries(
                asession, self.organization_id
            )
            if self.sender.country and self.sender.country.code in supported_countries:
                from_ph = random.choices(supported_countries[self.sender.country.code])[
                    0
                ]

                await self.conversation.aupdate(asession, phone_number_id=from_ph.id)
        else:
            from_ph = self.conversation.phone_number

        if not from_ph:
            return

        if receiver.phone_number and (
            provider_ids := await provider.create_message(
                from_ph.number, receiver.phone_number, self.body
            )
        ):
            self.provider_ids = provider_ids

        if commit is True:
            await self.asave(asession)


class Organization(Model):
    __abstract__ = False
    __tablename__ = "correspondence_organization"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(CountryType)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )
    owner: Mapped[User] = relationship(
        foreign_keys=[owner_id], viewonly=True, lazy="raise"
    )

    phone_numbers = relationship(
        "PhoneNumber",
        back_populates="organization",
        foreign_keys="PhoneNumber.organization_id",
    )

    @property
    def urls(self) -> dict[str, Any]:
        return {
            "web": {"detail": f"/organizations/{self.slug}"},
            "api": {
                "user_create": f"/api/organizations/{self.slug}/users/",
                "conversation_list": f"/api/organizations/{self.slug}/conversations/",
            },
        }

    @property
    def supported_countries(self) -> dict[str, list["PhoneNumber"]]:
        results = self.phone_numbers

        phone_numbers: dict[str, list["PhoneNumber"]] = defaultdict(list)

        for phone_number in results:
            if not phone_number.is_active:
                continue

            country_code = (
                phone_number.country.code
                if not isinstance(phone_number.country, str)
                else phone_number.country
            )

            phone_numbers[country_code].append(phone_number)

        return phone_numbers

    def is_viewable_by(self, user: User) -> bool:
        if self.owner_id == user.id:
            return True

        if user.is_staff and user.organization_id == self.id:
            return True

        return False

    async def get_conversations(
        self,
        asession: AsyncSession,
        pagination: QueryPaginationParams,
        manager: User | None = None,
    ) -> tuple[list[Any], int]:
        base_query = select(Conversation).filter(
            Conversation.organization_id == self.id
        )

        query = base_query.order_by(
            Conversation.unread.desc(),
            Conversation.last_message_at.desc(),
            Conversation.id.desc(),
        ).options(
            joinedload(Conversation.receiver),
            selectinload(Conversation.last_message).joinedload(Message.sender),
        )

        if manager:
            query = query.join(Conversation.receiver).filter(
                User.manager_id == manager.id
            )

        return await paginate(asession, Conversation.id, query, pagination)

    @classmethod
    async def get_supported_countries(
        cls, asession: AsyncSession, organization_id: int
    ) -> defaultdict[str, list[PhoneNumber]]:
        results = await PhoneNumber.repository(asession).aall(
            filter_by={"organization_id": organization_id}
        )
        phone_numbers = defaultdict(list)
        for phone_number in results:
            if not phone_number.is_active:
                continue

            country_code = phone_number.country.code
            phone_numbers[country_code].append(phone_number)

        return phone_numbers

    @classmethod
    async def get_from_phone_number(
        cls, asession: AsyncSession, phone_number: str
    ) -> Self | None:
        query = (
            select(cls)
            .join(PhoneNumber, cls.id == PhoneNumber.organization_id)
            .where(PhoneNumber.number == phone_number)
            .limit(1)
        )
        return await cls.repository(asession).aget_one_or_none(query)

    async def get_user_from_phone_number(
        self, asession: AsyncSession, phone_number: str
    ) -> "Optional[User]":
        return await User.repository(asession).aget_by(
            filter_by={"organization_id": self.id, "phone_number": phone_number},
            options=[joinedload(User.manager)],
        )


class Conversation(Model):
    __abstract__ = False
    __tablename__ = "correspondence_conversation"

    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )

    receiver: Mapped[User] = relationship(foreign_keys=[receiver_id], lazy="raise")

    messages_count: Mapped[int] = mapped_column(Integer, server_default="0")
    last_message_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    synced_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    unread: Mapped[bool] = mapped_column(Boolean, nullable=True, server_default="False")

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped[Optional[Organization]] = relationship(
        foreign_keys=[organization_id], viewonly=True, lazy="raise"
    )

    last_message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_message.id"),
        nullable=True,
    )

    last_message: Mapped[Message] = relationship(
        foreign_keys=[last_message_id], viewonly=True, lazy="raise"
    )

    phone_number_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_phone_number.id"),
        nullable=True,
    )

    phone_number: Mapped[PhoneNumber] = relationship(
        foreign_keys=[phone_number_id], viewonly=True, lazy="raise"
    )

    async def mark_as_read(self, asession: AsyncSession) -> None:
        await self.aupdate(asession, unread=False)

    async def mark_as_unread(self, asession: AsyncSession) -> None:
        await self.aupdate(asession, unread=True)

    async def get_messages(
        self, asession: AsyncSession, pagination: QueryPaginationParams
    ) -> tuple[list[Any], int]:
        query = (
            select(Message)
            .where(Message.conversation_id == self.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .options(selectinload(Message.sender))
        )

        messages, count = await paginate(asession, Message.id, query, pagination)
        for message in messages:
            message.conversation = self

        return messages, count

    async def get_last_message(self, asession: AsyncSession) -> Message | None:
        query = (
            select(Message)
            .where(Message.conversation_id == self.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )

        return await Message.repository(asession).aget_one_or_none(query)

    async def get_messages_count(self, asession: AsyncSession) -> int:
        return await Message.repository(asession).acount(
            filter_by={"conversation_id": self.id}
        )

    async def compute(
        self,
        asession: AsyncSession,
        last_message: Message | None = None,
        commit: bool = True,
    ):
        if not last_message:
            last_message = await self.get_last_message(asession)

        if last_message:
            self.last_message = last_message
            self.last_message_id = last_message.id
            self.last_message_at = last_message.created_at
            if self.last_message.sender_id == self.receiver_id:
                self.unread = True

        self.messages_count = await self.get_messages_count(asession)

        await self.asave(asession, commit=commit)

    async def create_message(
        self,
        asession: AsyncSession,
        sender: User,
        body: str,
        send: bool = True,
        extra_data: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> Message:
        async with asession.begin_nested():
            extra_data = extra_data or {}
            message = Message(
                sender=sender,
                sender_id=sender.id,
                body=body,
                conversation_id=self.id,
                conversation=self,
                organization_id=self.receiver.organization_id,
                **extra_data,
            )

            await message.asave(asession, commit=commit)
            await asession.flush()
            await self.compute(asession, last_message=message, commit=commit)

        if send:

            @event.listens_for(asession.sync_session, "after_commit", once=True)
            def after_commit(session: Session):
                loop = asyncio.get_running_loop()
                loop.create_task(message.async_send())

        return message

    async def has_automessage(
        self, asession: AsyncSession, automessage: AutoMessage
    ) -> bool:
        return await Message.repository(asession).aexists(
            clauses=[
                Message.automessage_id == automessage.id,
                Message.conversation_id == self.id,
            ]
        )
