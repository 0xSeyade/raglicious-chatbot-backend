import pytest
from uuid import uuid4

from collections.abc import Iterator
from typing import Callable

from datetime import datetime, timezone


from fastapi.testclient import TestClient

from app.application.chat.services import ChatResult
from app.domain.chat.entities import Message, MessageRole

from app.api.dependencies import get_chat_service
from app.core.exceptions import (
    LLMRateLimitError,
    LLMProviderUnavailableError,
    LLMAuthenticationError,
    LLMQuotaExceededError,
    ConversationNotFoundError,
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


class SuccessfulChatService:
    def __init__(self) -> None:
        self.conversation_id = uuid4()

    async def send_message(
        self,
        message: str,
        conversation_id=None,
    ) -> ChatResult:
        return ChatResult(
            conversation_id=conversation_id or self.conversation_id,
            response="Peace from AI, to you too!",
        )


class ConversationHistoryChatService:
    def __init__(self) -> None:
        self.conversation_id = uuid4()

    async def get_conversation_messages(
        self,
        conversation_id,
    ) -> list[Message]:
        if conversation_id != self.conversation_id:
            raise ConversationNotFoundError()

        now = datetime.now(timezone.utc)

        return [
            Message(
                id=uuid4(),
                conversation_id=self.conversation_id,
                role=MessageRole.USER,
                content="Peace",
                created_at=now,
            ),
            Message(
                id=uuid4(),
                conversation_id=self.conversation_id,
                role=MessageRole.ASSISTANT,
                content="Peace from AI, to you too!",
                created_at=now,
            ),
        ]


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


def test_chat_returns_new_conversation_id(
    client: TestClient,
    override_chat_service,
) -> None:
    service = SuccessfulChatService()
    override_chat_service(service)

    response = client.post(
        "api/v1/chat",
        json={
            "message": "Peace",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": str(service.conversation_id),
        "response": "Peace from AI, to you too!",
    }


def test_chat_returns_existing_conversation_id(
    client: TestClient,
    override_chat_service,
) -> None:
    service = SuccessfulChatService()
    override_chat_service(service)

    existing_conversation_id = uuid4()

    response = client.post(
        "api/v1/chat",
        json={
            "message": "Peace",
            "conversation_id": str(existing_conversation_id),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": str(existing_conversation_id),
        "response": "Peace from AI, to you too!",
    }


def test_chat_returns_conversation_history(
    client: TestClient,
    override_chat_service,
) -> None:
    service = ConversationHistoryChatService()
    override_chat_service(service)

    response = client.get(f"api/v1/chat/{service.conversation_id}/messages")

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": str(service.conversation_id),
        "messages": [
            {"role": "user", "content": "Peace"},
            {"role": "assistant", "content": "Peace from AI, to you too!"},
        ],
    }


def test_chat_returns_404_when_conversation_not_found(
    client: TestClient,
    override_chat_service,
) -> None:
    service = ConversationHistoryChatService()
    override_chat_service(service)

    response = client.get(f"api/v1/chat/{uuid4()}/messages")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "conversation_not_found"
