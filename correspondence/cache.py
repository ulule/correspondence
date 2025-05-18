from datetime import timedelta
from typing import Any, Optional

import cacheout
from redis import Redis
from redis.asyncio import Redis as AsyncRedis


class Cache:
    def get(self, key: str) -> Optional[Any]: ...

    async def aget(self, key: str) -> Optional[Any]: ...

    def set(self, key: str, value: Any, ex: timedelta | None = None) -> None: ...

    async def aset(self, key: str, value: Any, ex: timedelta | None = None) -> None: ...

    def ping(self): ...


class InMemoryCache(Cache):
    def __init__(self):
        self.cache = cacheout.Cache()

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    async def aget(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any, ex: timedelta | None = None) -> None:
        self.cache.set(key, value)

    async def aset(self, key: str, value: Any, ex: timedelta | None = None) -> None:
        return self.set(key, value)


class RedisCache(Cache):
    def __init__(self, sync_redis: Redis, async_redis: AsyncRedis):
        self.sync_redis = sync_redis
        self.async_redis = async_redis

    def ping(self):
        self.sync_redis.ping()

    def get(self, key: str) -> Optional[Any]:
        val = self.sync_redis.get(key)
        if val:
            return str(val)
        return None

    async def aget(self, key: str) -> Optional[Any]:
        val = await self.async_redis.get(key)
        if val:
            return str(val)
        return None

    def set(self, key: str, value: Any, ex: timedelta | None = None) -> None:
        self.sync_redis.set(key, px=ex, value=value)

    async def aset(self, key: str, value: Any, ex: timedelta | None = None) -> None:
        await self.async_redis.set(key, px=ex, value=value)
