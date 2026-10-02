from app.application.chat.ports import (
    LLMProvider,
    LLMRequest,
)


class ChatService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    async def send_message(self, message: str) -> str:
        request = LLMRequest(prompt=message)
        response = await self._llm_provider.generate(request)
        return response.content
