from fastapi import FastAPI

app = FastAPI(title="Raglicious AI Chatbot", version="1.0.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "OK"}
