from app.config.settings import settings
from app.graphs.product_search import ProductSearchAgent
from app.integrations.google_serper import LangChainGoogleSerperClient, MockGoogleSerperClient
from app.schemas.product_search import ProductSearchRequest, ProductSearchResponse


def build_product_search_agent() -> ProductSearchAgent:
    if settings.product_search_mode.lower() == "live":
        client = LangChainGoogleSerperClient(settings.google_serper_api_key)
        source = "google_serper"
    else:
        client = MockGoogleSerperClient()
        source = "mock_google_serper"

    return ProductSearchAgent(
        search_client=client,
        model_name=settings.ai_orchestration_model_name,
        result_source=source,
    )


async def search_products(criteria: ProductSearchRequest, request_id: str) -> ProductSearchResponse:
    return await build_product_search_agent().search(criteria, request_id)
