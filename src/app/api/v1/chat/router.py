from typing import Annotated
from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.api.v1.chat.schemas import (
    SendMessageRequest,
    SendMessageResponse,
)
from app.application.chat.services import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> SendMessageResponse:
    response = await chat_service.send_message(request.message)
    return SendMessageResponse(response=response)
