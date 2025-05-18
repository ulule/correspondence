from functools import cache
from typing import Any, ClassVar, Generic, Self, Sequence, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import Column, func
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.properties import MappedColumn
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.selectable import FromClause

from correspondence.db.sql import Select, delete, update
from correspondence.utils import utc_now

from .engine import AsyncSession
from .sql import exists, select

T = TypeVar("T", bound=Any)


class Repository(Generic[T]):
    session: AsyncSession
    klass: Type[T]

    def __init__(self, klass, session: AsyncSession):
        self.session = session
        self.klass = klass

    async def refresh_from_db(self, instance: T) -> T | None:
        return await self.aget(instance.pk)

    async def aget(
        self, id: Any, key: str = "id", options: list[ExecutableOption] | None = None
    ) -> T | None:
        return await self.aget_by(filter_by={key: id}, options=options)

    async def aget_by(
        self,
        filter_by: dict[str, Any] | None = None,
        options: list[ExecutableOption] | None = None,
        clauses: list[ColumnElement[bool]] | None = None,
    ) -> T | None:
        query = select(self.klass)
        if filter_by is not None:
            query = query.filter_by(**filter_by)
        if clauses:
            query = query.where(*clauses)
        if options:
            query = query.options(*options)

        return await self.aget_one_or_none(query)

    async def aget_one_or_none(self, statement: Select[tuple[T]]) -> T | None:
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def aall(
        self,
        limit: int | None = None,
        offset: int | None = None,
        filter_by: dict[str, Any] | None = None,
        order_by: InstrumentedAttribute | None = None,
        clauses: list[ColumnElement[bool]] | None = None,
    ) -> Sequence[T]:
        qs = select(self.klass)
        if limit is not None:
            qs = qs.limit(limit)
        if offset is not None:
            qs = qs.offset(offset)
        if order_by is not None:
            qs = qs.order_by(order_by)
        if filter_by is not None:
            qs = qs.filter_by(**filter_by)
        if clauses:
            qs = qs.where(*clauses)
        return await self.aget_all(qs)

    async def acount(
        self,
        filter_by: dict[str, Any] | None = None,
        *clause: ColumnElement[bool],
    ) -> int:
        qs = select(func.count(self.klass.pk_column()))
        if filter_by is not None:
            qs = qs.filter_by(**filter_by)
        if clause:
            qs = qs.where(*clause)

        res = await self.session.scalar(qs)
        return res or 0

    async def aget_all(self, statement: Select[tuple[T]]) -> Sequence[T]:
        result = await self.session.execute(statement)
        return result.scalars().unique().all()

    async def aexists(self, clauses: list[ColumnElement[bool]]) -> bool:
        res = await self.session.scalar(exists().where(*clauses).select())
        return bool(res)

    async def aget_or_404(
        self,
        id: Any,
        key: str = "id",
        options: list[ExecutableOption] | None = None,
    ) -> T:
        return await self.aget_by_or_404(filter_by={key: id}, options=options)

    async def aget_by_or_404(self, **kw: Any) -> T:
        instance = await self.aget_by(**kw)
        if not instance:
            raise HTTPException(
                status_code=404, detail=f"{self.klass.__name__} not found"
            )

        return instance

    async def acreate(
        self,
        commit: bool = True,
        **values: Any,
    ) -> T:
        instance = self.klass()
        instance.fill(**values)

        created = await instance.asave(self.session, commit=commit)
        return created

    async def asave(
        self,
        instance: T,
        commit: bool = True,
    ) -> T:
        self.session.add(instance)
        if commit and not self.session.in_nested_transaction():
            await self.session.commit()

        return instance

    async def abulk_update(
        self,
        filter_by: dict[str, Any] | None = None,
        clauses: list[ColumnElement[bool]] | None = None,
        **values: Any,
    ) -> None:
        query = update(self.klass)
        if filter_by:
            query = query.filter_by(**filter_by)
        if clauses:
            query = query.where(*clauses)
        query = query.values(**values)
        await self.session.execute(query)
        await self.session.flush()

    async def abulk_delete(
        self,
        filter_by: dict[str, Any] | None = None,
        clauses: list[ColumnElement[bool]] | None = None,
    ) -> None:
        query = delete(self.klass)
        if filter_by:
            query = query.filter_by(**filter_by)
        if clauses:
            query = query.where(*clauses)
        await self.session.execute(query)
        await self.session.flush()

    async def asoft_delete(self, id: int) -> None:
        stmt = (
            update(self.klass)
            .where(
                self.klass.pk_column() == id,
                getattr(self.klass, "deleted_at").is_(None),
            )
            .values(
                deleted_at=utc_now(),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def aget_or_create(
        self,
        options: list[ExecutableOption] | None = None,
        defaults: dict[str, Any] | None = None,
        **params: Any,
    ) -> tuple[T, bool]:
        instance = await self.aget_by(options=options, filter_by=params)
        if not instance:
            if defaults is not None:
                params.update(defaults)
            return await self.acreate(**params), True

        return instance, False

    async def adelete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.commit()


class ModelMixin:
    __mutables__: set[Column[Any]] | set[str] | None = None
    __table__: ClassVar[FromClause]

    @property
    def pk(self) -> str:
        return getattr(self, "id")

    @classmethod
    def pk_column(cls):
        return getattr(cls, "id")

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
    def repository(cls, asession: AsyncSession) -> Repository[Self]:
        return Repository(cls, asession)

    async def adelete(self, asession: AsyncSession) -> None:
        return await self.repository(asession).adelete(self)

    async def aupdate(
        self,
        asession: AsyncSession,
        **values: Any,
    ) -> None:
        model = self.__class__
        return await model.repository(asession).abulk_update(
            filter_by={"id": self.pk}, **values
        )

    async def refresh_from_db(self, asession: AsyncSession) -> Self | None:
        return await self.repository(asession).refresh_from_db(self)

    async def asave(
        self,
        asession: AsyncSession,
        commit: bool = True,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
        **values: Any,
    ) -> Self:
        if not include:
            include = self.get_mutable_keys()
        updated = self.fill(include=include, exclude=exclude, **values)
        return await self.repository(asession).asave(updated, commit=commit)

    def to_dict(self) -> dict[str, Any]:
        columns = []
        if hasattr(self, "__table__"):
            columns = self.__table__.c.keys()

        ret = dict([(column, getattr(self, column)) for column in columns])
        return ret
