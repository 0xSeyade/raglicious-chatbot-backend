import pytest

from app.application.chat.ports import LLMRequest
from app.infrastructure.llm.openai_provider import OpenAIProvider


class MockResponse:
    output_text = "Peace from the mock OpenAI response"


class MockClient:
    async def create_response(
        self,
        *,
        model: str,
        input: str,
    ) -> MockResponse:
        return MockResponse


@pytest.mark.asyncio
async def test_generate_returns_llm_response() -> None:
    client = MockClient()
    provider = OpenAIProvider(
        client=client,
        model="test model",
    )
    response = await provider.generate(
        LLMRequest(prompt="Peace"),
    )

    assert response.content == "Peace from the mock OpenAI response"
