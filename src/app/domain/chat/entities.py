from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import StrEnum


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class Conversation:
    id: UUID
    conversation_id: UUID
    updated_at: datetime


@dataclass(frozen=True)
class Message:
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
