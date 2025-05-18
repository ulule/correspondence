import os
from enum import Enum
from typing import Optional

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    development = "development"
    testing = "testing"
    staging = "staging"
    production = "production"


class Broker(str, Enum):
    inmemory = "inmemory"
    redis = "redis"


class Cache(str, Enum):
    inmemory = "inmemory"
    redis = "redis"


class Settings(BaseSettings):
    SENTRY_DSN: str | None = None
    DEFAULT_COUNTRY: str = "FR"
    SESSION_COOKIE_NAME: str = "correspondence_session"
    SESSION_COOKIE_AGE: int = 60 * 60 * 24 * 31  # 31 days
    ENV: Environment = Environment.development
    HEROKU_DATABASE_URL: PostgresDsn | None = None
    DATABASE_URL: PostgresDsn
    CACHE_BACKEND: str = Cache.inmemory
    CACHE_REDIS_URL: Optional[RedisDsn] = None
    BROKER_BACKEND: str = Broker.inmemory
    BROKER_REDIS_URL: Optional[RedisDsn] = None
    BROKER_RESULT_BACKEND: str = Broker.inmemory
    BROKER_RESULT_REDIS_URL: Optional[RedisDsn] = None
    DEBUG: bool = False
    SECRET: str = "super secret jwt secret"
    LOG_LEVEL: str = "INFO"
    LOG_JSON_FORMAT: bool = False
    SMS_PROVIDER_CLASS: str = "correspondence.provider.NoopProvider"
    SMS_PROVIDER_ACCOUNT: str = ""
    SMS_PROVIDER_TOKEN: str = ""


env = Environment(os.getenv("CORRESPONDENCE_API_ENV", Environment.development))
env_file = f".env.{env.name}"

settings = Settings(_env_file=env_file, ENV=env)  # type: ignore
