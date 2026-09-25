from typing import Annotated

from fastapi import Depends

from app.application.chat.ports import LLMProvider
from app.application.chat.services import ChatService
from app.infrastructure.llm.mock import MockLLMProvider


def get_llm_provider() -> LLMProvider:
    return MockLLMProvider()


def get_chat_service(
    llm_provider: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> ChatService:
    return ChatService(llm_provider)
