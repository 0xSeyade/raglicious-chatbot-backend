import pytest

from app.application.chat.services import ChatService


class MockTestLLM:
    async def generate(self, prompt: str) -> str:
        return f"AI Test response to: {prompt}"


@pytest.mark.asyncio
async def test_send_message_returns_llm_response() -> None:
    llm_provider = MockTestLLM()
    chat_service = ChatService(llm_provider)
    response = await chat_service.send_message("Peace my sister")

    assert response == "AI Test response to: Peace my sister"
