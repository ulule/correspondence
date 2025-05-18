from typing import AsyncGenerator, Generator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_asession(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.db.async_session_local() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


def get_db_session(request: Request) -> Generator:
    try:
        db = request.app.db.session_local()
        yield db
    finally:
        db.close()  # type: ignore
