import time
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

logger = structlog.get_logger()


async def request_context_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    request_id = str(uuid4())
    start_time = time.perf_counter()

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
    )

    logger.info(
        "http_request_started",
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        logger.exception(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
        )
        raise

    finally:
        structlog.contextvars.clear_contextvars()
