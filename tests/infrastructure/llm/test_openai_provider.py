import pytest
import httpx

from unittest.mock import AsyncMock, patch
from openai import APIStatusError
from openai.types.responses import ResponseInputParam

from app.application.chat.ports import LLMRequest, LLMMessage, MessageRole
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.retry import RetryPolicy
from app.core.exceptions import LLMRateLimitError


class MockResponse:
    output_text = "Peace from the mock OpenAI response"


class MockClient:
    def __init__(self) -> None:
        self.model: str | None = None
        self.input: ResponseInputParam | None = None

    async def create_response(
        self,
        *,
        model: str,
        input: ResponseInputParam,
    ) -> MockResponse:
        self.model = model
        self.input = input
        return MockResponse()


@pytest.mark.asyncio
async def test_generate_returns_llm_response() -> None:
    client = MockClient()

    provider = OpenAIProvider(
        client=client,
        model="test-model",
    )

    response = await provider.generate(
        LLMRequest(
            messages=[
                LLMMessage(
                    role=MessageRole.USER,
                    content="Peace",
                ),
                LLMMessage(
                    role=MessageRole.ASSISTANT,
                    content="Peace from AI, to you too!",
                ),
                LLMMessage(
                    role=MessageRole.USER,
                    content="What do you think of Person of Interest?",
                ),
            ],
        )
    )

    assert response.content == "Peace from the mock OpenAI response"
    assert client.model == "test-model"
    assert client.input == [
        {
            "role": "user",
            "content": "Peace",
        },
        {
            "role": "assistant",
            "content": "Peace from AI, to you too!",
        },
        {
            "role": "user",
            "content": "What do you think of Person of Interest?",
        },
    ]


@pytest.mark.asyncio
async def test_generate_retries_after_503() -> None:
    class RetryMockClient:
        def __init__(self) -> None:
            self.attempts = 0

        async def create_response(
            self,
            *,
            model: str,
            input: ResponseInputParam,
        ) -> MockResponse:
            self.attempts += 1

            if self.attempts == 1:
                request = httpx.Request(
                    "POST",
                    "https://api.openai.com/v1/responses",
                )

                response = httpx.Response(
                    status_code=503,
                    request=request,
                )

                raise APIStatusError(
                    "Service unavailable.",
                    response=response,
                    body=None,
                )

            return MockResponse()

    client = RetryMockClient()
    provider = OpenAIProvider(
        client=client,
        model="test-model",
    )

    with patch(
        "app.infrastructure.llm.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        response = await provider.generate(
            LLMRequest(
                messages=[
                    LLMMessage(
                        role=MessageRole.USER,
                        content="Peace",
                    ),
                ]
            )
        )

    assert response.content == "Peace from the mock OpenAI response"
    assert client.attempts == 2


@pytest.mark.asyncio
async def test_generate_retries_after_429() -> None:
    class RateLimitedMockClient:
        def __init__(self) -> None:
            self.attempts = 0

        async def create_response(
            self,
            *,
            model: str,
            input: ResponseInputParam,
        ) -> MockResponse:
            self.attempts += 1

            if self.attempts == 1:
                request = httpx.Request(
                    "POST",
                    "https://api.openai.com/v1/responses",
                )

                response = httpx.Response(
                    status_code=429,
                    request=request,
                )

                raise APIStatusError(
                    "Rate limit exceeded.",
                    response=response,
                    body=None,
                )

            return MockResponse()

    client = RateLimitedMockClient()
    provider = OpenAIProvider(
        client=client,
        model="test-model",
    )

    with patch(
        "app.infrastructure.llm.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        result = await provider.generate(
            LLMRequest(
                messages=[
                    LLMMessage(
                        role=MessageRole.USER,
                        content="Peace",
                    ),
                ]
            )
        )

    assert result.content == "Peace from the mock OpenAI response"
    assert client.attempts == 2


@pytest.mark.asyncio
async def test_generate_raises_llm_rate_limit_retries_exhausted() -> None:
    class AlwaysRateLimitedClient:
        def __init__(self) -> None:
            self.attempts = 0

        async def create_response(
            self,
            *,
            model: str,
            input: ResponseInputParam,
        ) -> MockResponse:
            self.attempts += 1

            request = httpx.Request(
                "POST",
                "https://api.openai.com/v1/responses",
            )

            response = httpx.Response(
                status_code=429,
                request=request,
            )

            raise APIStatusError(
                "Rate limit exceeded.",
                response=response,
                body=None,
            )

    client = AlwaysRateLimitedClient()

    provider = OpenAIProvider(
        client=client,
        model="test-model",
        retry_policy=RetryPolicy(
            max_attempts=3,
            base_delay=0.1,
            jitter=0.0,
        ),
    )

    with patch(
        "app.infrastructure.llm.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ) as mock_sleep:
        with pytest.raises(LLMRateLimitError):
            await provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(
                            role=MessageRole.USER,
                            content="Peace",
                        ),
                    ]
                )
            )

    assert client.attempts == 3
    assert mock_sleep.await_count == 2
