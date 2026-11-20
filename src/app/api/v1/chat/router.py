from typing import Annotated
from fastapi import APIRouter, Depends
from uuid import UUID

from app.api.dependencies import get_chat_service
from app.api.v1.chat.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    ConversationHistoryResponse,
    MessageResponse,
)
from app.application.chat.services import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> SendMessageResponse:
    result = await chat_service.send_message(
        message=request.message,
        conversation_id=request.conversation_id,
    )
    return SendMessageResponse(
        conversation_id=result.conversation_id,
        response=result.response,
    )


@router.get("/{conversation_id}/messages", response_model=ConversationHistoryResponse)
async def get_conversation_messages(
    conversation_id: UUID,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> ConversationHistoryResponse:
    messages = await chat_service.get_conversation_messages(conversation_id)

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[
            MessageResponse(
                role=message.role.value,
                content=message.content,
            )
            for message in messages
        ],
    )
