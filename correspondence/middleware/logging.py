import json
import time
from typing import Any

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request
from starlette.routing import Match
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from uvicorn.protocols.utils import get_path_with_query_string


class WrappedReceive:
    request: Request
    receive: Receive
    body: dict[str, Any] | None

    def __init__(self, request: Request, receive: Receive):
        self.request = request
        self.receive = receive
        self.body = None

    async def handle(self) -> Message:
        message = await self.receive()
        if self.request.headers.get("content-type") == "application/json" and (
            body := message.get("body")
        ):
            try:
                self.body = json.loads(body)
            except Exception:
                pass

        return message


class LoggingMiddleware:
    app: ASGIApp
    logger: structlog.stdlib.BoundLogger

    def __init__(
        self,
        app: ASGIApp,
        *,
        logger: structlog.stdlib.BoundLogger,
    ):
        self.app = app
        self.logger = logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        structlog.contextvars.clear_contextvars()
        # These context vars will be added to all log entries emitted during the request
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        request = Request(scope, receive, send)

        app = self.app.app  # type: ignore

        matching_route = None
        for route in app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                matching_route = route
            elif match == Match.PARTIAL:
                matching_route = route

        start_time = time.perf_counter_ns()

        async def custom_send(message: Message):
            if message["type"] == "http.response.start":
                if status_code := message.get("status"):
                    scope["status_code"] = status_code

            await send(message)

        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        wrapped_receive = WrappedReceive(request, receive)
        try:
            await self.app(scope, wrapped_receive.handle, custom_send)
        except Exception as exc:
            raise exc
        finally:
            status_code = scope.get("status_code") or 500
            process_time = (time.perf_counter_ns() - start_time) / 10**9
            url = get_path_with_query_string(scope)  # type: ignore
            client_host = ""
            client_port = 0
            if request.client:
                client_host = request.client.host
                client_port = request.client.port
            http_method = request.method
            http_version = request.scope["http_version"]

            recorded_queries = request.app.db.get_recorded_queries()  # type: ignore
            process_time = sum(
                [recorded_query.duration for recorded_query in recorded_queries]
            )

            params = {
                "url": str(request.url),
                "status_code": status_code,
                "path": request.url.path,
                "method": http_method,
                "request_id": request_id,
                "version": http_version,
                "client_ip": client_host,
                "client_port": client_port,
                "duration": process_time,
                "database_queries_count": len(recorded_queries),
                "database_queries_duration": process_time,
            }

            if matching_route is not None:
                params["route"] = matching_route.name

            if wrapped_receive.body:
                params["payload"] = wrapped_receive.body

            self.logger.info(
                f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                **params,
            )
