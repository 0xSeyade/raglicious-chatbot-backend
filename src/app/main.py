from fastapi import FastAPI

from app.api.v1.chat.router import router as chat_router
from app.api.v1.health.router import router as health_router
from app.core.config import get_settings
from app.api.exception_handlers import (
    handle_llm_authentication,
    handle_llm_provider_unavailable,
    handle_llm_quota,
    handle_llm_rate_limit,
    handle_unexpected_error,
)
from app.core.exceptions import (
    LLMAuthenticationError,
    LLMProviderUnavailableError,
    LLMQuotaExceededError,
    LLMRateLimitError,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_exception_handler(LLMRateLimitError, handle_llm_rate_limit)
app.add_exception_handler(LLMAuthenticationError, handle_llm_authentication)
app.add_exception_handler(LLMProviderUnavailableError, handle_llm_provider_unavailable)
app.add_exception_handler(LLMQuotaExceededError, handle_llm_quota)
app.add_exception_handler(Exception, handle_unexpected_error)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
