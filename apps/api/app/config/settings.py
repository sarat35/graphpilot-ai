from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "buyseconds"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    aws_profile: str = "default"
    aws_region: str = "us-east-1"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    database_url: str = ""
    redis_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
