import sqlite3
from abc import (
    ABC,
    abstractmethod
)
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from config import settings
from logger import logger

@dataclass
class TelegramUser:
    telegram_user_id: str
    agent_service_user_id: str
    onboarded_successfully: bool
    created_at: str
    updated_at: str


class Database(ABC):
    @abstractmethod
    def get_user_by_telegram_user_id(self, telegram_user_id: str) -> Optional[TelegramUser]:
        pass

    @abstractmethod
    def set_onboard_successfully(self, telegram_user_id: str, onboard_successfully: bool):
        pass

    @abstractmethod
    def add_new_user(self, telegram_user: TelegramUser):
        pass


class SqliteDB(Database):
    def __init__(self):
        self.db_file_path = settings.SQLITE_DB_FILE_PATH
        self.timeout = settings.SQLITE_DB_TIMEOUT_SECONDS

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_file_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def add_new_user(self, telegram_user: TelegramUser):
        query = """
        INSERT INTO telegram_users (
            telegram_user_id, agent_service_user_id, onboarded_successfully, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, (
                    telegram_user.telegram_user_id,
                    telegram_user.agent_service_user_id,
                    telegram_user.onboarded_successfully,
                    telegram_user.created_at,
                    telegram_user.updated_at
                ))
                logger.info(f"Added new user: {telegram_user.telegram_user_id}")
        except sqlite3.IntegrityError:
            logger.warning(f"User {telegram_user.telegram_user_id} already exists.")
        except Exception as e:
            logger.error(f"Error adding user {telegram_user.telegram_user_id}: {e}")

    def get_user_by_telegram_user_id(self, telegram_user_id: str) -> Optional[TelegramUser]:
        query = "SELECT * FROM telegram_users WHERE telegram_user_id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(query, (telegram_user_id,))
                row = cursor.fetchone()
                if row:
                    return TelegramUser(
                        telegram_user_id=row["telegram_user_id"],
                        agent_service_user_id=row["agent_service_user_id"],
                        onboarded_successfully=bool(row["onboarded_successfully"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"]
                    )
        except Exception as e:
            logger.error(f"Error getting user {telegram_user_id}: {e}")
        return None

    def set_onboard_successfully(self, telegram_user_id: str, onboard_successfully: bool):
        query = "UPDATE telegram_users SET onboarded_successfully = ?, updated_at = ? WHERE telegram_user_id = ?"
        updated_at = datetime.now().isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(query, (onboard_successfully, updated_at, telegram_user_id))
                logger.info(f"Updated onboarding status for user: {telegram_user_id}")
        except Exception as e:
            logger.error(f"Error updating onboarding status for user {telegram_user_id}: {e}")
