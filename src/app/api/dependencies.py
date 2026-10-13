from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.chat.ports import LLMProvider
from app.application.chat.repositories import ConversationRepository
from app.application.chat.services import ChatService
from app.core.config import get_settings
from app.infrastructure.database.repositories.conversation import (
    PostgresConversationRepository,
)
from app.infrastructure.database.session import get_db_session
from app.infrastructure.llm.openai_client import OpenAIClient
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.application.chat.transactions import TransactionManager
from app.infrastructure.database.transactions import (
    SqlAlchemyTransactionManager,
)


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    client = OpenAIClient(settings)
    return OpenAIProvider(
        client=client,
        model=settings.openai_model,
    )


def get_conversation_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationRepository:
    return PostgresConversationRepository(session)


def get_transaction_manager(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TransactionManager:
    return SqlAlchemyTransactionManager(session)


def get_chat_service(
    llm_provider: Annotated[
        LLMProvider,
        Depends(get_llm_provider),
    ],
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    transaction_manager: Annotated[
        TransactionManager,
        Depends(get_transaction_manager),
    ],
) -> ChatService:
    return ChatService(
        llm_provider=llm_provider,
        conversation_repository=conversation_repository,
        transaction_manager=transaction_manager,
    )
