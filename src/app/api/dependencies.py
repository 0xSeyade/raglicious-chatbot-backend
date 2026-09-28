from typing import Annotated

from fastapi import Depends

from app.application.chat.ports import LLMProvider
from app.application.chat.services import ChatService
from app.core.config import get_settings
from app.infrastructure.llm.openai_client import OpenAIClient
from app.infrastructure.llm.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    client = OpenAIClient(settings)
    return OpenAIProvider(
        client=client,
        model=settings.openai_model,
    )


def get_chat_service(
    llm_provider: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> ChatService:
    return ChatService(llm_provider)
