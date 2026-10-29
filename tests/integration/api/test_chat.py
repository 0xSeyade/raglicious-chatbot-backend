import pytest

from collections.abc import Iterator
from typing import Callable


from fastapi.testclient import TestClient

from app.api.dependencies import get_chat_service
from app.core.exceptions import (
    LLMRateLimitError,
    LLMProviderUnavailableError,
    LLMAuthenticationError,
    LLMQuotaExceededError,
)
from app.main import app


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
    override_chat_service(FailingChatService(exception))

    response = client.post(
        "api/v1/chat",
        json={"message": "Peace"},
    )

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
