from typing import Literal, TypedDict

from openai import AsyncOpenAI
from openai.types.responses import Response

from app.core.config import Settings


class OpenAIMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(self, messages: list[OpenAIMessage]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        return response.choices[0].message.content or ""

    async def create_response(
        self,
        *,
        model: str,
        input: str,
    ) -> Response:
        return await self._client.responses.create(model=model, input=input)
