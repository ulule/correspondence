import json
import time
from typing import Callable

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from uvicorn.protocols.utils import get_path_with_query_string


class AsyncIteratorWrapper:
    """The following is a utility class that transforms a
    regular iterable to an asynchronous one.

    link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: FastAPI, *, logger: structlog.BoundLogger, log_response: bool = False
    ):
        self.app = app
        self.logger = logger
        self.log_response = log_response

        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        structlog.contextvars.clear_contextvars()
        # These context vars will be added to all log entries emitted during the request
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        app = request.app

        matching_route = None
        for route in app.router.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                matching_route = route
            elif match == Match.PARTIAL:
                matching_route = route

        start_time = time.perf_counter_ns()
        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        response = None
        try:
            response = await call_next(request)
        except Exception as exc:
            raise exc
        else:
            return response
        finally:
            process_time = (time.perf_counter_ns() - start_time) / 10**9
            status_code = 500
            if response:
                status_code = response.status_code
            url = get_path_with_query_string(request.scope)
            client_host = request.client.host  # type: ignore
            client_port = request.client.port  # type: ignore
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

            try:
                body = await request.json()
                params["payload"] = body
            except Exception:
                body = None

            if self.log_response and response is not None:
                bodies = [
                    section async for section in response.__dict__["body_iterator"]
                ]
                response.__setattr__("body_iterator", AsyncIteratorWrapper(bodies))
                resp_body = ""

                try:
                    resp_body = json.loads(bodies[0].decode())
                except Exception:
                    resp_body = str("".join(bodies))

                if resp_body:
                    params["body"] = resp_body

            self.logger.info(
                f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                **params,
            )
