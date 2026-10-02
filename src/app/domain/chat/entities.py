from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Message:
    id: UUID
    content: str
    role: str
    created_at: datetime
