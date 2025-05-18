from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import CountryType

from correspondence.db.models import Model


class User(Model):
    __abstract__ = False
    __tablename__ = "correspondence_user"

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
    messages_sent_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default="0"
    )
    messages_received_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default="0"
    )
    manager_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=True,
    )
    manager: Mapped["Optional[User]"] = relationship(foreign_keys=[manager_id])

    conversation: Mapped["Conversation"] = relationship(
        back_populates="receiver",
        uselist=False,
        foreign_keys="Conversation.receiver_id",
    )


class Message(Model):
    __abstract__ = False
    __tablename__ = "correspondence_message"

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )
    sender: Mapped[User] = relationship(foreign_keys=[sender_id])

    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_conversation.id"),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", foreign_keys=[conversation_id]
    )


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
    owner: Mapped[User] = relationship(foreign_keys=[owner_id])


class Conversation(Model):
    __abstract__ = False
    __tablename__ = "correspondence_conversation"

    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_user.id"),
        nullable=False,
    )

    receiver: Mapped[User] = relationship(foreign_keys=[receiver_id])

    messages_count: Mapped[int | None] = mapped_column(Integer, server_default="0")
    last_message_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    synced_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    unread: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default="False"
    )

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("correspondence_organization.id"),
        nullable=True,
    )

    organization: Mapped[Organization] = relationship(foreign_keys=[organization_id])
