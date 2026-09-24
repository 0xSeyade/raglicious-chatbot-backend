class FakeLLMProvider:
    async def generate(self, prompt: str) -> str:
        return f"AI response to: {prompt}"
