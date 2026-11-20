from uuid import UUID

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: UUID | None = None


class SendMessageResponse(BaseModel):
    conversation_id: UUID
    response: str


class MessageResponse(BaseModel):
    role: str
    content: str


class ConversationHistoryResponse(BaseModel):
    conversation_id: UUID
    messages: list[MessageResponse]
