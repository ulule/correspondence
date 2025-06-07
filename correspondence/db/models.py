from datetime import datetime
from typing import TypeVar

from sqlalchemy import INTEGER, TIMESTAMP, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils import force_auto_coercion, force_instant_defaults

from correspondence.utils import utc_now

from .mixins import ModelMixin

force_auto_coercion()
force_instant_defaults()

my_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_N_label)s",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
        "pk": "%(table_name)s_pkey",
    }
)

make_searchable(my_metadata)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    metadata = my_metadata


class TimestampedModel(BaseModel):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=utc_now,
        nullable=False,
        default=utc_now,
    )


class Model(TimestampedModel, ModelMixin, AsyncAttrs):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        INTEGER,
        primary_key=True,
    )


ModelType = TypeVar("ModelType", bound=Model)
