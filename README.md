# raglicious-chatbot-backend

Chatbot API, powered by AI with RAG: Backend

To run project run:

- `uv run uvicorn app.main:app --reload`

To run tests (unit, integration, etc.):

- General: `uv run pytest`
- Show all tests: `uv run pytest -v --tb=short`
- Specific file: `uv run pytest tests/integration/api/test_chat.py`
- Specific file, and show all its tests: `uv run pytest tests/integration/api/test_chat.py -v --tb=short`
