from fastapi import FastAPI

from app.api.v1.chat.router import router as chat_router
from app.api.v1.health.router import router as health_router

app = FastAPI(title="Raglicious AI Chatbot", version="1.0.0")

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
