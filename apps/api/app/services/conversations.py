from uuid import UUID

from fastapi import HTTPException, status

from app.config.settings import settings
from app.graphs.conversation import build_conversation_graph
from app.repositories.mock_conversations import MockConversationRepository
from app.schemas.conversations import ConversationDetail, ConversationMessageInput
from app.schemas.product_search import FuelType, ProductSearchRequest
from app.services.product_search import search_products

mock_conversation_repository = MockConversationRepository()
conversation_graph = build_conversation_graph()


async def create_conversation(user_id: UUID) -> ConversationDetail:
    record = await mock_conversation_repository.create(user_id)
    return ConversationDetail.model_validate(record.detail(settings.intelligence_model_name))


async def get_conversation(user_id: UUID, conversation_id: UUID) -> ConversationDetail:
    record = await mock_conversation_repository.get(conversation_id, user_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationDetail.model_validate(record.detail(settings.intelligence_model_name))


async def send_message(
    user_id: UUID, conversation_id: UUID, payload: ConversationMessageInput
) -> ConversationDetail:
    record = await mock_conversation_repository.get(conversation_id, user_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    await mock_conversation_repository.add_message(record, "user", payload.content)
    graph_result = await conversation_graph.ainvoke(
        {"message": payload.content, "criteria": record.criteria}
    )
    record.criteria = graph_result.get("criteria", record.criteria)
    city = record.criteria.get("city")
    if city:
        fuel_type = record.criteria.get("fuel_type")
        criteria = ProductSearchRequest(
            city=city.title(), fuel_type=FuelType(fuel_type) if fuel_type else None
        )
        search = await search_products(criteria, str(conversation_id))
        if search.results:
            links = "\n".join(
                f"{index + 1}. {result.title} — {result.source_url}"
                for index, result in enumerate(search.results)
            )
            reply = f"Top {len(search.results)} value matches in {city.title()}:\n{links}"
        else:
            reply = (
                f"I could not find city-specific matches for {city.title()}. "
                "Try adding a budget or brand."
            )
    else:
        reply = graph_result["reply"]
    await mock_conversation_repository.add_message(record, "assistant", reply)
    return ConversationDetail.model_validate(record.detail(settings.intelligence_model_name))
