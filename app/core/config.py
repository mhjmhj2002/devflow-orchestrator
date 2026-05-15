from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "Agentic Platform"

    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""

    # Webhook secret used to validate incoming GitHub webhook deliveries
    GITHUB_WEBHOOK_SECRET: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    DEBUG: bool = True

    # allow extra environment variables present in the environment (e.g. for local tooling)
    model_config = {"extra": "allow"}


settings = Settings()