from dataclasses import dataclass
from uuid import UUID

from app.application.chat.ports import (
    LLMProvider,
    LLMRequest,
)

from app.application.chat.transactions import TransactionManager
from app.application.chat.repositories import ConversationRepository
from app.core.exceptions import ConversationNotFoundError
from app.domain.chat.entities import MessageRole


@dataclass(frozen=True)
class ChatResult:
    conversation_id: UUID
    response: str


class ChatService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        conversation_repository: ConversationRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._llm_provider = llm_provider
        self._conversation_repository = conversation_repository
        self._transaction_manager = transaction_manager

    async def send_message(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> ChatResult:
        if conversation_id is None:
            conversation = await self._conversation_repository.create_conversation()
        else:
            conversation = await self._conversation_repository.get_conversation(
                conversation_id
            )

            if conversation is None:
                raise ConversationNotFoundError()

        try:
            await self._conversation_repository.add_message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=message,
            )

            await self._transaction_manager.commit()

        except Exception:
            await self._transaction_manager.rollback()
            raise

        try:
            llm_response = await self._llm_provider.generate(LLMRequest(prompt=message))

            await self._conversation_repository.add_message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=llm_response.content,
            )

            await self._transaction_manager.commit()

        except Exception:
            await self._transaction_manager.rollback()
            raise

        return ChatResult(
            conversation_id=conversation.id,
            response=llm_response.content,
        )

        # request = LLMRequest(prompt=message)
        # response = await self._llm_provider.generate(request)
        # return response.content
