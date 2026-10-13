import pytest

from collections.abc import Iterator
from typing import Callable


from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider, get_chat_service
from app.core.exceptions import (
    LLMRateLimitError,
    LLMProviderUnavailableError,
    LLMAuthenticationError,
    LLMQuotaExceededError,
)
from app.main import app

# class RateLimitedLLM:
#     async def generate(self, request):
#         raise LLMRateLimitError("The LLM provider rate limit was exceeded.")


# class UnavailableLLM:
#     async def generate(self, request):
#         raise LLMProviderUnavailableError("Provider unavailable.")


# class AutheticationErrorLLM:
#     async def generate(self, request):
#         raise LLMAuthenticationError("Authentication failed.")


# class QuotaExceededErrorLLM:
#     async def generate(self, request):
#         raise LLMQuotaExceededError("Quota is exceeded.")


class FailingLLM:
    def __init__(self, error: Exception) -> None:
        self._error = error

    async def generate(self, request):
        raise self._error


class FailingChatService:
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def send_message(
        self,
        message: str,
        conversation_id=None,
    ):
        raise self.error


@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def override_chat_service() -> Iterator[Callable[[object], None]]:
    original_overrides = app.dependency_overrides.copy()

    def override(service: object) -> None:
        app.dependency_overrides[get_chat_service] = lambda: service

    yield override

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.mark.parametrize(
    ("exception", "expected_status", "expected_code"),
    [
        (
            LLMAuthenticationError(),
            503,
            "llm_provider_configuration_error",
        ),
        (
            LLMRateLimitError(),
            429,
            "llm_rate_limited",
        ),
        (
            LLMProviderUnavailableError(),
            503,
            "llm_provider_unavailable",
        ),
        (
            LLMQuotaExceededError(),
            503,
            "llm_quota_exceeded",
        ),
    ],
)
def test_chat_handles_llm_errors(
    client: TestClient,
    exception: Exception,
    expected_status: int,
    expected_code: str,
    override_chat_service,
) -> None:
    # app.dependency_overrides[get_llm_provider] = lambda: FailingLLM(exception)
    override_chat_service(FailingChatService(exception))

    with TestClient(app) as client:
        response = client.post(
            "api/v1/chat",
            json={"message": "Peace"},
        )

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code


# def test_chat_returns_429_when_llm_rate_limited(
#     client: TestClient,
# ) -> None:
#     response = client.post(
#         "/api/v1/chat",
#         json={"message": "Hello"},
#     )

#     assert response.status_code == 429

#     assert response.json() == {
#         "error": {
#             "code": "llm_rate_limited",
#             "message": (
#                 "The chatbot service is temporarily busy. " "Please try again shortly."
#             ),
#         }
#     }
