from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    TELEGRAM_WEBHOOK_PORT: int

    AGENT_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()