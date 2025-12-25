from datetime import datetime

from database import (
    TelegramUser,
    SqliteDB,
)

def add_new_telegram_user(
        telegram_user_id: str,
        agent_service_user_id: str,
        onboarded_successfully: bool = True,
        created_at: str | None = None,
        updated_at: str | None = None,
):
    if created_at is None:
        created_at = datetime.now().isoformat()

    if updated_at is None:
        updated_at = datetime.now().isoformat()

    telegram_user = TelegramUser(
        telegram_user_id=telegram_user_id,
        agent_service_user_id=agent_service_user_id,
        onboarded_successfully=onboarded_successfully,
        created_at=created_at,
        updated_at=updated_at,
    )

    db = SqliteDB()
    db.add_new_user(telegram_user)
