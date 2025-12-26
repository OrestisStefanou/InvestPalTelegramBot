import datetime as dt
from dataclasses import dataclass

from telegram import Bot
from telegram.error import TelegramError

from agent_service_client import AgentServiceClient
from database import Database, TelegramUserDbModel
import utils
from logger import logger
from config import settings


@dataclass
class TelegramUser:
    telegram_user_id: str
    first_name: str


class BotService():
    def __init__(self, database: Database):
        self.agent_service_client = AgentServiceClient()
        self.database = database

    async def handle_new_user(self, telegram_user: TelegramUser):
        user_onboarded_successfully = True
        try:
            await self._onboard_user_on_agent_service(telegram_user)
        except Exception:
            user_onboarded_successfully = False

        self._store_user_in_database(telegram_user, user_onboarded_successfully)


    async def generate_bot_response(self, telegram_user: TelegramUser, message: str) -> list[str]:
        # Check and handle any errors that may have happened in start command handler
        try:
            await self._check_and_handle_onboarding_error(telegram_user)
        except Exception:
            return self._get_error_message_response()

        session_id = self._create_agent_service_session_id(telegram_user.telegram_user_id)

        try:
            ai_response = await self.agent_service_client.generate_ai_response(
                session_id=session_id,
                message=message,
            )
        except Exception as e:
            logger.error(f"Failed to generate ai response: {e}")
            return self._get_error_message_response()

        response_messages = []
        for msg_chunk in utils.split_ai_response_message(ai_response):
            if msg_chunk == "":
                continue

            telegram_html_msg = utils.markdown_to_telegram_html(msg_chunk)
            if telegram_html_msg == "":
                continue

            response_messages.append(telegram_html_msg)

        return response_messages

    async def _check_and_handle_onboarding_error(self, telegram_user: TelegramUser):
        db_user = self.database.get_user_by_telegram_user_id(telegram_user.telegram_user_id)
        if not db_user:
            await self._onboard_user_on_agent_service(telegram_user)
            self._store_user_in_database(telegram_user, True)
            return None

        if db_user.onboarded_successfully:
            return None

        await self._onboard_user_on_agent_service(telegram_user)
        self.database.set_onboarded_successfully(telegram_user.telegram_user_id, True)
        return None

    async def _onboard_user_on_agent_service(self, telegram_user: TelegramUser):
        agent_service_user_id = self._create_agent_service_user_id(telegram_user.telegram_user_id)
        session_id = self._create_agent_service_session_id(telegram_user.telegram_user_id)

        try:
            await self.agent_service_client.create_user_context(
                user_id=agent_service_user_id,
                user_profile={
                    "first_name": telegram_user.first_name,
                }
            )
        except Exception as e:
            logger.error(f"Failed to create user context: {e}")
            raise e

        try:
            await self.agent_service_client.create_session(
                user_id=agent_service_user_id,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise e

    async def send_adhoc_message(self, telegram_user_id: str, message: str):
        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=telegram_user_id, text=message)
            logger.info(f"Message sent successfully to user {telegram_user_id}")
        except TelegramError as e:
            logger.error(f"Failed to send message to user {telegram_user_id}: {e}")
            raise e

    def _store_user_in_database(self, telegram_user: TelegramUser, onboarded_successfully: bool):
        try:
            self.database.add_new_user(
                TelegramUserDbModel(
                    telegram_user_id=telegram_user.telegram_user_id,
                    agent_service_user_id=self._create_agent_service_user_id(telegram_user.telegram_user_id),
                    user_first_name=telegram_user.first_name,
                    onboarded_successfully=onboarded_successfully,
                    created_at=dt.datetime.now().isoformat(),
                    updated_at=dt.datetime.now().isoformat(),
                )
            )
        except Exception as e:
            logger.error(f"Failed to store user on database: {e}")
            raise e

    def _create_agent_service_user_id(self, telegram_user_id: str) -> str:
        return f"telegram:{telegram_user_id}"

    def _create_agent_service_session_id(self, telegram_user_id: str) -> str:
        return f"telegram_session:{telegram_user_id}"

    def _get_error_message_response(self) -> list[str]:
        return ["I am sorry, something went wrong. Please try again later."]
