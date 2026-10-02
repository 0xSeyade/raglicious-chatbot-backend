import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMQuotaExceededError,
)

logger = logging.getLogger(__name__)


async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled application error",
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occured.",
            }
        },
    )


async def handle_llm_rate_limit(
    request: Request,
    exc: LLMRateLimitError,
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "llm_rate_limited",
                "message": (
                    "The chatbot service is temporarily busy. "
                    "Please try again shortly."
                ),
            }
        },
    )


async def handle_llm_provider_unavailable(
    request: Request,
    exc: LLMProviderUnavailableError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "llm_provider_unavailable",
                "message": (
                    "The chatbot is temporarily unavailable. " "Please try again later."
                ),
            }
        },
    )


async def handle_llm_authentication(
    request: Request,
    exc: LLMAuthenticationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "llm_provider_configuration_error",
                "message": "The chatbot service is currently unavailable.",
            }
        },
    )


async def handle_llm_quota(
    request: Request,
    exc: LLMQuotaExceededError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "llm_quota_exceeded",
                "message": ("The chatbot service is currently unavailable."),
            }
        },
    )
