from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentMember, get_current_member
from app.schemas.conversations import ConversationDetail, ConversationMessageInput
from app.services.conversations import create_conversation, get_conversation, send_message

router = APIRouter()
Member = Annotated[CurrentMember, Depends(get_current_member)]


@router.post("", response_model=ConversationDetail)
async def create_member_conversation(member: Member) -> ConversationDetail:
    return await create_conversation(member.id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_member_conversation(conversation_id: UUID, member: Member) -> ConversationDetail:
    return await get_conversation(member.id, conversation_id)


@router.post("/{conversation_id}/messages", response_model=ConversationDetail)
async def send_member_message(
    conversation_id: UUID, payload: ConversationMessageInput, member: Member
) -> ConversationDetail:
    return await send_message(member.id, conversation_id, payload)
