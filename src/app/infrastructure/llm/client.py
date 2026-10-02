from typing import Protocol
from openai.types.responses import Response


class LLMClient(Protocol):
    async def create_response(
        self,
        *,
        model: str,
        input: str,
    ) -> Response: ...
