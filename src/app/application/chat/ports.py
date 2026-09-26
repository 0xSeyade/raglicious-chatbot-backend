from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    prompt: str


@dataclass(frozen=True)
class LLMResponse:
    content: str


class LLMProvider(Protocol):
    async def generate(self, prompt: LLMRequest) -> LLMResponse: ...
