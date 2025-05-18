from enum import Enum as BaseEnum
from functools import cache
from typing import Any, ClassVar, Self, Sequence  # type: ignore

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, inspect
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.orm.properties import MappedColumn
from sqlalchemy.sql.selectable import FromClause
from sqlalchemy_utils import ChoiceType

from correspondence.utils import Enum

from .engine import AsyncSession
from .sql import exists, select


class ModelMixin:
    __mutables__: set[Column[Any]] | set[str] | None = None
    __table__: ClassVar[FromClause]
    asession: AsyncSession | None = None

    @classmethod
    def create(
        cls,
        session: Session,
        autocommit: bool = True,
        **values: Any,
    ) -> Self:
        instance = cls()
        instance.fill(**values)

        created = instance.save(session, autocommit=autocommit)
        return created

    @classmethod
    def from_payload(cls, schema: BaseModel, **values: Any) -> Self:
        instance = cls()
        params: dict[str, Any] = {}
        for k, v in schema.__class__.__signature__.parameters.items():
            introspection = inspect(cls)
            if introspection is None:
                continue

            column = getattr(introspection.columns, k)
            value = getattr(schema, k)
            if type(value) is getattr(column.type, "python_type"):
                params[k] = value
            elif issubclass(v.annotation, BaseEnum):
                if not isinstance(column.type, ChoiceType):
                    continue
                if not hasattr(column.type, "choices"):
                    continue
                if not issubclass(column.type.choices, Enum):  # type: ignore
                    continue

                choices = column.type.choices.choices()
                params[k] = choices[value.name]

        instance = instance.fill(**dict(params, **values))
        return instance

    def update(
        self,
        session: Session,
        autocommit: bool = True,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
        **values: Any,
    ) -> Self:
        if not include:
            include = self.get_mutable_keys()
        updated = self.fill(include=include, exclude=exclude, **values)
        res = updated.save(session, autocommit=autocommit)
        return res

    def fill(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
        **values: Any,
    ) -> Self:
        exclude = exclude if exclude else set()
        for col, value in values.items():
            if not hasattr(self, col):
                raise Exception(f"has no attr: {col}")

            if isinstance(include, set) and col not in include:
                continue

            if col not in exclude:
                setattr(self, col, value)
        return self

    def save(self, session: Session, autocommit: bool = True) -> Self:
        session.add(self)
        if autocommit:
            session.commit()
        return self

    @classmethod
    async def aget(
        cls, asession: AsyncSession, id: Any, key: str = "id"
    ) -> Self | None:
        params = {}
        params[key] = id
        return await cls.aget_by(asession, **params)

    @classmethod
    def get(cls, session: Session, id: Any, key: str = "id") -> Self | None:
        params = {}
        params[key] = id
        return cls.get_by(session, **params)

    @classmethod
    async def aall(
        cls,
        session: AsyncSession,
        limit: int | None = None,
        offset: int | None = None,
        filter_by: dict[str, Any] | None = None,
        order_by: InstrumentedAttribute | None = None,
    ) -> Sequence[Self]:
        qs = select(cls)
        if limit is not None:
            qs = qs.limit(limit)
        if offset is not None:
            qs = qs.offset(offset)
        if order_by is not None:
            qs = qs.order_by(order_by)
        if filter_by is not None:
            qs = qs.filter_by(**filter_by)
        res = await session.scalars(qs)

        instances = res.unique().all()
        for instance in instances:
            instance.asession = session

        return instances

    @classmethod
    async def aexists(cls, session: AsyncSession, id: Any, key: str = "id") -> bool:
        res = await session.scalar(exists().where(getattr(cls, key) == id).select())
        return bool(res)

    @classmethod
    async def aget_or_404(
        cls, id: Any, key: str = "id", asession: AsyncSession | None = None
    ) -> Self:
        params = {}
        params[key] = id
        params["asession"] = asession
        return await cls.aget_by_or_404(**params)

    @classmethod
    async def aget_by(
        cls,
        asession: AsyncSession,
        **params: Any,
    ) -> Self | None:
        query = select(cls).filter_by(**params)
        res = await asession.execute(query)
        return res.scalars().unique().one_or_none()

    @classmethod
    def get_by(
        cls,
        session: Session,
        **params: Any,
    ) -> Self | None:
        query = select(cls).filter_by(**params)
        res = session.execute(query)
        return res.scalars().unique().one_or_none()

    @classmethod
    async def aget_by_or_404(
        cls,
        **params: Any,
    ) -> Self:
        instance = await cls.aget_by(**params)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{cls.__name__} not found")

        return instance

    @classmethod
    @cache
    def get_mutable_keys(cls) -> set[str]:
        def name(c: str | MappedColumn[Any] | Column[Any]) -> str:
            if isinstance(c, str):
                return c
            if hasattr(c, "name"):
                return c.name
            raise Exception("no mutable key name found")

        columns = cls.__mutables__
        if columns is not None:
            return set(name(column) for column in columns)

        columnNames = {c.name for c in cls.__table__.c}
        pks = {pk.name for pk in cls.__table__.primary_key}
        return columnNames - pks

    @classmethod
    async def acreate(
        cls,
        asession: AsyncSession,
        autocommit: bool = True,
        **values: Any,
    ) -> Self:
        instance = cls()
        instance.asession = values.pop("session", None)
        instance.fill(**values)

        created = await instance.asave(asession, autocommit=autocommit)
        return created

    async def aupdate(
        self,
        asession: AsyncSession,
        autocommit: bool = True,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
        **values: Any,
    ) -> Self:
        if not include:
            include = self.get_mutable_keys()
        updated = self.fill(include=include, exclude=exclude, **values)
        res = await updated.asave(asession, autocommit=autocommit)
        return res

    async def asave(self, asession: AsyncSession, autocommit: bool = True) -> Self:
        asession.add(self)
        if autocommit:
            await asession.commit()
        return self

    def to_dict(self) -> dict[str, Any]:
        columns = []
        if hasattr(self, "__table__"):
            columns = self.__table__.c.keys()

        ret = dict([(column, getattr(self, column)) for column in columns])
        return ret
