from typing import Any, Generic, Self, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select, func, over
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from correspondence.db.models import ModelType

T = TypeVar("T", bound=Any)


class QueryPaginationParams(BaseModel):
    limit: int = Field(20, gt=0, le=100)
    offset: int | None = None
    starting_after: int | None = None
    ending_before: int | None = None
    q: str | None = None
    is_staff: bool | None = None
    manager_id: int | None = None


async def paginate(
    asession: AsyncSession,
    pk_column: InstrumentedAttribute,
    statement: Select[tuple[ModelType]],
    pagination: QueryPaginationParams,
) -> tuple[list[ModelType], int]:
    limit = pagination.limit
    offset = pagination.offset
    if pagination.starting_after:
        statement = statement.filter(pk_column > pagination.starting_after)
    if pagination.ending_before:
        statement = statement.filter(pk_column < pagination.ending_before)
    statement = statement.limit(limit + 1)
    if offset:
        statement = statement.offset(offset)
    statement = statement.add_columns(over(func.count()))

    result = await asession.execute(statement)
    rows = result.unique().all()

    results: list[ModelType] = []
    count = 0
    for item, count in rows:
        count = int(count)
        results.append(item)

    return results, count


class PageMetaResource(BaseModel):
    limit: int
    offset: int | None = None
    starting_after: int | None = None
    ending_before: int | None = None
    total: int
    next: str


class PageResource(BaseModel, Generic[T]):
    data: list[T]
    meta: PageMetaResource

    @classmethod
    def from_results(
        cls, params: QueryPaginationParams, items: list[T], total: int
    ) -> Self:
        next_url = f"?limit={params.limit}"
        if params.offset:
            next_url += f"&offset={params.offset + params.limit}"
        if len(items) > params.limit:
            next_url += f"&starting_after={items[-1].id}"
            items = items[: params.limit]

        return cls(
            data=items,
            meta=PageMetaResource(
                limit=params.limit,
                offset=params.offset,
                total=total,
                next=next_url,
            ),
        )
