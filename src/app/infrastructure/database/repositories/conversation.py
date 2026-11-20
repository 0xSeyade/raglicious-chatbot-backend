from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.chat.repositories import ConversationRepository
from app.domain.chat.entities import Conversation, Message, MessageRole
from app.infrastructure.database.models.chat import (
    ConversationModel,
    MessageModel,
)


class PostgresConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_conversation(self) -> Conversation:
        model = ConversationModel()

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_conversation(model)

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        model = MessageModel(
            conversation_id=conversation_id,
            role=role.value,
            content=content,
        )

        self._session.add(model)

        conversation = await self._session.get(
            ConversationModel,
            conversation_id,
        )

        if conversation is not None:
            conversation.updated_at = datetime.now(timezone.utc)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_message(model)

    async def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        model = await self._session.get(
            ConversationModel,
            conversation_id,
        )

        if model is None:
            return None

        return self._to_conversation(model)

    async def get_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        statement = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(
                MessageModel.created_at.asc(),
                MessageModel.id.asc(),
            )
        )

        result = await self._session.execute(statement)

        return [self._to_message(model) for model in result.scalar().all()]

    @staticmethod
    def _to_conversation(
        model: ConversationModel,
    ) -> Conversation:
        return Conversation(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_message(
        model: MessageModel,
    ) -> Message:
        return Message(
            id=model.id,
            conversation_id=model.conversation_id,
            role=MessageRole(model.role),
            content=model.content,
            created_at=model.created_at,
        )
