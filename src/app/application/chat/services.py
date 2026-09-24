from app.application.chat.ports import LLMProvider


class ChatService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    async def send_message(self, message: str) -> str:
        return await self._llm_provider.generate(message)
