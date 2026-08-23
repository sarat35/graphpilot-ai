from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    id: UUID
    status: str
    criteria: dict[str, str] = Field(default_factory=dict)
    last_message_at: datetime


class ConversationMessageInput(BaseModel):
    content: str = Field(min_length=1, max_length=2_000)


class ConversationMessage(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationDetail(BaseModel):
    conversation: Conversation
    messages: list[ConversationMessage]
    model_name: str
