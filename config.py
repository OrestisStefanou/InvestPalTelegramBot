from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    TELEGRAM_WEBHOOK_PORT: int

    AGENT_SERVICE_URL: str

    SQLITE_DB_FILE_PATH: str = "telegram_bot_db.sqlite"
    SQLITE_DB_TIMEOUT_SECONDS: int = 10

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()