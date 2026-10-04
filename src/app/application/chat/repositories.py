from typing import Protocol
from uuid import UUID

from app.domain.chat.entities import (
    MessageRole,
    Message,
    Conversation,
)


class ConversationRepository(Protocol):
    async def create_conversation(self) -> Conversation: ...

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message: ...

    async def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None: ...

    async def get_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]: ...
