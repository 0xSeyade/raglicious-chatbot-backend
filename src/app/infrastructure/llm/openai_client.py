from openai import AsyncOpenAI
from openai.types.responses import Response

from app.core.config import Settings


class OpenAIClient:
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
        )

    async def create_response(
        self,
        *,
        model: str,
        input: str,
    ) -> Response:
        return await self._client.responses.create(model=model, input=input)
