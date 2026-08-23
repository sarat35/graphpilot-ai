from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.conversations import Conversation, ConversationMessage


@dataclass
class MockConversationRecord:
    id: UUID
    user_id: UUID
    criteria: dict[str, str] = field(default_factory=dict)
    messages: list[ConversationMessage] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def detail(self, model_name: str):
        return {
            "conversation": Conversation(
                id=self.id, status="active", criteria=self.criteria, last_message_at=self.updated_at
            ),
            "messages": self.messages,
            "model_name": model_name,
        }


class MockConversationRepository:
    def __init__(self) -> None:
        self._records: dict[UUID, MockConversationRecord] = {}

    async def create(self, user_id: UUID) -> MockConversationRecord:
        record = MockConversationRecord(id=uuid4(), user_id=user_id)
        self._records[record.id] = record
        return record

    async def get(self, conversation_id: UUID, user_id: UUID) -> MockConversationRecord | None:
        record = self._records.get(conversation_id)
        return record if record and record.user_id == user_id else None

    async def add_message(
        self, record: MockConversationRecord, role: str, content: str
    ) -> ConversationMessage:
        message = ConversationMessage(
            id=uuid4(), role=role, content=content, created_at=datetime.now(UTC)
        )
        record.messages.append(message)
        record.updated_at = message.created_at
        return message

    def clear(self) -> None:
        self._records.clear()
