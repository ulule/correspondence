import logging
import pathlib
import sys
from contextlib import asynccontextmanager
from typing import Awaitable, Callable, Self  # type: ignore

import jinja2
import sentry_sdk
import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from ddtrace.contrib.asgi import TraceMiddleware
from ddtrace.trace import tracer
from fastapi import FastAPI as BaseFastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from structlog.types import EventDict, Processor
from taskiq import InMemoryBroker, TaskiqEvents, TaskiqMiddleware, TaskiqState
from taskiq.abc.broker import AsyncBroker
from taskiq.abc.result_backend import AsyncResultBackend
from taskiq.result_backends.dummy import DummyResultBackend
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from correspondence.api.endpoints import router as api_router
from correspondence.builtins.extensions import CorrespondenceExtension
from correspondence.cache import Cache, InMemoryCache, RedisCache
from correspondence.conf import Broker as BrokerSettings
from correspondence.conf import Cache as CacheSettings
from correspondence.conf import Environment, Settings
from correspondence.db.engine import DatabaseEngine
from correspondence.middleware.logging import LoggingMiddleware
from correspondence.provider import Provider
from correspondence.utils import import_string
from correspondence.web.automessage import router as automessage_router
from correspondence.web.hooks import router as hooks_router
from correspondence.web.root import router as root_router


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    if not app.broker.is_worker_process:
        await app.broker.startup()
    yield
    if not app.broker.is_worker_process:
        await app.broker.shutdown()


root_dir = pathlib.Path(__file__).resolve().parent


class FastAPI(BaseFastAPI):
    broker: AsyncBroker
    cache: Cache
    db: DatabaseEngine
    settings: Settings
    provider: Provider
    templates = type[Jinja2Templates]

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        app = cls(lifespan=lifespan, debug=settings.DEBUG)
        app.settings = settings
        app.mount("/static", StaticFiles(directory=root_dir / "static"), name="static")
        app.include_router(root_router)
        app.include_router(automessage_router)
        app.include_router(api_router)
        app.include_router(hooks_router)
        app.setup_logging()
        app.setup_database()
        app.setup_templates()
        app.setup_error_reporting()

        if settings.ENV != Environment.testing:
            app.add_middleware(
                LoggingMiddleware, logger=structlog.stdlib.get_logger("http.request")
            )
        app.add_middleware(CorrelationIdMiddleware)

        tracing_middleware = next(
            (m for m in app.user_middleware if m.cls == TraceMiddleware), None
        )
        if tracing_middleware is not None:
            app.user_middleware = [
                m for m in app.user_middleware if m.cls != TraceMiddleware
            ]
            structlog.stdlib.get_logger("api.datadog_patch").info(
                "Patching Datadog tracing middleware to be the outermost middleware..."
            )
            app.user_middleware.insert(0, tracing_middleware)
            app.middleware_stack = app.build_middleware_stack()

        app.setup_broker()
        app.setup_cache()
        app.setup_provider()

        return app

    def setup_error_reporting(self):
        if not self.settings.SENTRY_DSN:
            return

        sentry_sdk.init(
            dsn=self.settings.SENTRY_DSN,
            send_default_pii=True,
        )

    def setup_templates(self):
        loader = jinja2.FileSystemLoader(root_dir / "templates")
        template_env = jinja2.Environment(loader=loader, autoescape=True)
        template_env.extensions.update(
            {"correspondence": CorrespondenceExtension(template_env, app=self)}
        )

        self.templates = Jinja2Templates(env=template_env)

    def setup_provider(self):
        klass = import_string(self.settings.SMS_PROVIDER_CLASS)

        self.provider = klass(
            account=self.settings.SMS_PROVIDER_ACCOUNT,
            token=self.settings.SMS_PROVIDER_TOKEN,
        )

    def setup_database(self):
        engine = DatabaseEngine(
            self.settings.HEROKU_DATABASE_URL or self.settings.DATABASE_URL
        )
        engine.ping()
        self.db = engine

    def setup_cache(self):
        cache = Cache()
        if self.settings.CACHE_BACKEND == CacheSettings.inmemory:
            cache = InMemoryCache()
        elif (
            self.settings.CACHE_BACKEND == CacheSettings.redis
            and self.settings.CACHE_REDIS_URL
        ):
            async_redis = AsyncRedis.from_url(str(self.settings.CACHE_REDIS_URL))
            sync_redis = Redis.from_url(str(self.settings.CACHE_REDIS_URL))
            cache = RedisCache(sync_redis, async_redis)

        cache.ping()

        self.cache = cache

    def startup_event_generator(self) -> Callable[[TaskiqState], Awaitable[None]]:
        async def startup(state: TaskiqState) -> None:
            if not self.broker.is_worker_process:
                return

            state.fastapi_app = self
            self.router.routes = []
            await self.router.startup()

        return startup

    def shutdown_event_generator(self) -> Callable[[TaskiqState], Awaitable[None]]:
        async def startup(_: TaskiqState) -> None:
            if not self.broker.is_worker_process:
                return

            await self.router.shutdown()

        return startup

    def setup_broker(self):
        class Middleware(TaskiqMiddleware):
            pass

        result_backend: AsyncResultBackend = DummyResultBackend()
        if self.settings.BROKER_RESULT_BACKEND == BrokerSettings.redis:
            result_backend = RedisAsyncResultBackend(
                redis_url=str(self.settings.BROKER_RESULT_REDIS_URL),  # type: ignore
                result_ex_time=600,  # 10 minutes expiration
            )

        self.broker = InMemoryBroker()
        if self.settings.BROKER_BACKEND == BrokerSettings.redis:
            self.broker = ListQueueBroker(
                url=str(self.settings.BROKER_REDIS_URL),
            ).with_result_backend(result_backend)
            self.broker.add_middlewares(Middleware())

        self.broker.add_event_handler(
            TaskiqEvents.WORKER_STARTUP,
            self.startup_event_generator(),
        )

        self.broker.add_event_handler(
            TaskiqEvents.WORKER_SHUTDOWN,
            self.shutdown_event_generator(),
        )

    def setup_logging(self):
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

        timestamper = structlog.processors.TimeStamper(fmt="iso")

        shared_processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            drop_color_message_key,
            tracer_injection,
            timestamper,
            structlog.processors.StackInfoRenderer(),
        ]

        if self.settings.LOG_JSON_FORMAT:
            # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
            # `message` key but the pretty ConsoleRenderer looks for `event`
            shared_processors.append(rename_event_key)
            # Format the exception only for JSON logs, as we want to pretty-print them when
            # using the ConsoleRenderer
            shared_processors.append(structlog.processors.format_exc_info)

        structlog.configure(
            processors=shared_processors
            + [
                # Prepare event dict for `ProcessorFormatter`.
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        log_renderer: structlog.types.Processor
        if self.settings.LOG_JSON_FORMAT:
            log_renderer = structlog.processors.JSONRenderer()
        else:
            log_renderer = structlog.dev.ConsoleRenderer()

        formatter = structlog.stdlib.ProcessorFormatter(
            # These run ONLY on `logging` entries that do NOT originate within
            # structlog.
            foreign_pre_chain=shared_processors,
            # These run on ALL entries after the pre_chain is done.
            processors=[
                # Remove _record & _from_structlog.
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                log_renderer,
            ],
        )

        handler = logging.StreamHandler()
        # Use OUR `ProcessorFormatter` to format all `logging` entries.
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(self.settings.LOG_LEVEL.upper())

        for _log in ["uvicorn", "uvicorn.error"]:
            # Clear the log handlers for uvicorn loggers, and enable propagation
            # so the messages are caught by our root logger and formatted correctly
            # by structlog
            logging.getLogger(_log).handlers.clear()
            logging.getLogger(_log).propagate = True

        # Since we re-create the access logs ourselves, to add all information
        # in the structured log (see the `logging_middleware` in main.py), we clear
        # the handlers and prevent the logs to propagate to a logger higher up in the
        # hierarchy (effectively rendering them silent).
        logging.getLogger("uvicorn.access").handlers.clear()
        logging.getLogger("uvicorn.access").propagate = False

        def handle_exception(exc_type, exc_value, exc_traceback):
            """
            Log any uncaught exception instead of letting it be printed by Python
            (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
            See https://stackoverflow.com/a/16993115/3641865
            """
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            root_logger.error(
                "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
            )

        sys.excepthook = handle_exception


# https://github.com/hynek/structlog/issues/35#issuecomment-591321744
def rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Log entries keep the text message in the `event` field, but Datadog
    uses the `message` field. This processor moves the value from one field to
    the other.
    See https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def tracer_injection(_, __, event_dict: EventDict) -> EventDict:
    # get correlation ids from current tracer context
    span = tracer.current_span()
    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

    # add ids to structlog event dictionary
    event_dict["dd.trace_id"] = str(trace_id or 0)
    event_dict["dd.span_id"] = str(span_id or 0)

    return event_dict
