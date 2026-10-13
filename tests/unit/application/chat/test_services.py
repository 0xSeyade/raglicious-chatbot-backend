import pytest
from uuid import UUID, uuid4

from datetime import datetime, timezone

from app.application.chat.ports import LLMRequest, LLMResponse
from app.application.chat.services import ChatService, ChatResult
from app.core.exceptions import (
    ConversationNotFoundError,
    LLMProviderUnavailableError,
)
from app.domain.chat.entities import Conversation, Message, MessageRole


class MockLLMProvider:
    def __init__(self, response: str = "Peace from AI") -> None:
        self.response = response
        self.requests: list[LLMRequest] = []
        self.error: Exception | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)

        if self.error is not None:
            raise self.error

        return LLMResponse(content=self.response)


class MockConversationRepository:
    def __init__(self) -> None:
        self.conversations: dict[UUID, Conversation] = {}
        self.messages: list[Message] = []
        self.pending_messages: list[Message] = []
        self.created_count = 0

    async def create_conversation(self) -> Conversation:
        now = datetime.now(timezone.utc)
        conversation = Conversation(
            id=uuid4(),
            created_at=now,
            updated_at=now,
        )
        self.conversations[conversation.id] = conversation
        self.created_count += 1
        return conversation

    async def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        return self.conversations.get(conversation_id)

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        self.pending_messages.append(message)
        return message

    async def get_messages(self, conversation_id: UUID) -> list[Message]:

        return [
            message
            for message in self.messages + self.pending_messages
            if message.conversation_id == conversation_id
        ]


class MockTransactionManager:
    def __init__(
        self,
        repository: MockConversationRepository,
    ) -> None:
        self.repository = repository
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self) -> None:
        self.repository.messages.extend(self.repository.pending_messages)
        self.repository.pending_messages.clear()
        self.commit_count += 1

    async def rollback(self) -> None:
        self.repository.pending_messages.clear()
        self.rollback_count += 1


@pytest.fixture
def dependencies() -> tuple[
    MockLLMProvider,
    MockConversationRepository,
    MockTransactionManager,
    ChatService,
]:
    llm = MockLLMProvider()
    repository = MockConversationRepository()
    transactions = MockTransactionManager(repository)

    service = ChatService(
        llm_provider=llm,
        conversation_repository=repository,
        transaction_manager=transactions,
    )

    return llm, repository, transactions, service


@pytest.mark.asyncio
async def test_send_message_creates_conversation_and_persists_messages(
    dependencies,
) -> None:
    llm, repository, transactions, service = dependencies

    result = await service.send_message("Peace")

    assert isinstance(result, ChatResult)
    assert isinstance(result.conversation_id, UUID)
    assert result.response == "Peace from AI"

    assert repository.created_count == 1
    assert len(repository.messages) == 2

    user_message, assistant_message = repository.messages

    assert user_message.conversation_id == result.conversation_id
    assert user_message.role == MessageRole.USER
    assert user_message.content == "Peace"

    assert assistant_message.conversation_id == result.conversation_id
    assert assistant_message.role == MessageRole.ASSISTANT
    assert assistant_message.content == "Peace from AI"

    assert llm.requests == [LLMRequest(prompt="Peace")]
    assert transactions.commit_count == 2
    assert transactions.rollback_count == 0


@pytest.mark.asyncio
async def test_send_message_reuses_existing_conversation(
    dependencies,
) -> None:
    _, repository, transactions, service = dependencies

    conversation = await repository.create_conversation()

    result = await service.send_message(
        "Follow-up question",
        conversation_id=conversation.id,
    )

    assert result.conversation_id == conversation.id
    assert repository.created_count == 1
    assert len(repository.messages) == 2
    assert transactions.commit_count == 2


@pytest.mark.asyncio
async def test_send_message_raises_when_conversation_not_found(
    dependencies,
) -> None:
    llm, repository, transactions, service = dependencies

    unknown_id = uuid4()

    with pytest.raises(ConversationNotFoundError):
        await service.send_message(
            "Peace",
            conversation_id=unknown_id,
        )

    assert repository.created_count == 0
    assert repository.messages == []
    assert llm.requests == []
    assert transactions.commit_count == 0


@pytest.mark.asyncio
async def test_send_message_preserves_user_message_when_llm_fails(
    dependencies,
) -> None:
    llm, repository, transactions, service = dependencies

    llm.error = LLMProviderUnavailableError()

    with pytest.raises(LLMProviderUnavailableError):
        await service.send_message("Peace")

    assert repository.created_count == 1
    assert len(repository.messages) == 1

    user_message = repository.messages[0]

    assert user_message.role == MessageRole.USER
    assert user_message.content == "Peace"

    assert transactions.commit_count == 1
    assert transactions.rollback_count == 1
