from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    app_name: str = "buyseconds"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    # One model is deliberately shared by LangGraph and every product-search agent.
    ai_orchestration_model_name: str = "gpt-5.4-mini"
    intelligence_model_name: str = "gpt-5.4-mini"  # Backwards-compatible setting for chat.
    product_search_research_system_prompt: str = (
        "You research public Hyderabad used-car listings. "
        "Use only approved sources and never invent data."
    )
    product_search_ranking_system_prompt: str = (
        "You explain deterministic used-car ranking results "
        "without changing their calculated scores."
    )
    product_search_allowed_city: str = "Hyderabad"
    product_search_allowed_domains: str = "cars24.com,carwale.com,cartrade.com,spinny.com,olx.in"
    product_search_max_candidates: int = 100
    product_search_top_results: int = 10
    product_search_mode: str = "mock"
    google_serper_api_key: str = ""
    google_serper_base_url: str = "https://google.serper.dev/search"

    aws_profile: str = "default"
    aws_region: str = "us-east-1"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    database_url: str = ""
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str = ""
    supabase_service_role_key: str = ""
    supabase_secret_key: str = ""
    cors_origins: str = "http://localhost:3000"
    redis_url: str = ""

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        extra="ignore",
    )


settings = Settings()
