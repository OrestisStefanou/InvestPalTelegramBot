from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    TELEGRAM_WEBHOOK_PORT: int
    # Will only respond to messages coming from this user id
    TELEGRAM_USER_ID: str

    INVESTPAL_BACKEND_URL: str
    INVESTPAL_BACKEND_TIMEOUT_MINUTES: int = 5
    # Optional: Set this to use an existing InvestPal user ID.
    # If not provided, a new user will be created using the Telegram user ID.
    INVESTPAL_USER_ID: str | None = None
    # If given these will be sent in the headers of the InvestPal /chat endpoint
    # in order for the agent to have access to your alpaca and coinbase account
    ALPACA_API_KEY: str | None = None
    ALPACA_API_SECRET: str | None = None
    COINBASE_API_KEY: str | None = None
    COINBASE_API_SECRET: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()