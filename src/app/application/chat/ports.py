from dataclasses import dataclass
from typing import Protocol

from app.domain.chat.entities import MessageRole


@dataclass(frozen=True)
class LLMMessage:
    role: MessageRole
    content: str


@dataclass(frozen=True)
class LLMRequest:
    messages: list[LLMMessage]


@dataclass(frozen=True)
class LLMResponse:
    content: str


class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
