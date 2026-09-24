from fastapi import APIRouter

from app.api.v1.chat.schemas import (
    SendMessageRequest,
    SendMessageResponse,
)
from app.application.chat.services import ChatService
from app.infrastructure.llm.fake import FakeLLMProvider

router = APIRouter(prefix="/chat", tags=["chat"])

llm_provider = FakeLLMProvider()
chat_service = ChatService(llm_provider)


@router.post("", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest) -> SendMessageResponse:
    response = await chat_service.send_message(request.message)
    return SendMessageResponse(response=response)
