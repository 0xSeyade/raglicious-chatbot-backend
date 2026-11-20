from typing import Protocol
from openai.types.responses import Response, ResponseInputParam


class LLMClient(Protocol):
    async def create_response(
        self,
        *,
        model: str,
        input: ResponseInputParam,
    ) -> Response: ...
