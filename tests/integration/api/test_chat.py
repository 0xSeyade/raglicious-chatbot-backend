import pytest

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
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


@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


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
) -> None:
    app.dependency_overrides[get_llm_provider] = lambda: FailingLLM(exception)

    response = client.post(
        "api/v1/chat",
        json={"message": "Peace"},
    )

    print(response.json())

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
