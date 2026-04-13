from dataclasses import dataclass

from telegram import Bot
from telegram.error import TelegramError

from investpal_client import InvestPalClient
import utils
from logger import logger
from config import settings


@dataclass
class TelegramUser:
    telegram_id: str
    first_name: str


class BotService():
    def __init__(self):
        self.investpal_client = InvestPalClient()
        self._onboarded: bool = False

    async def handle_new_user(self, telegram_user: TelegramUser):
        try:
            await self._onboard_user_on_investpal(telegram_user)
            self._onboarded = True
        except Exception:
            self._onboarded = False

    async def generate_bot_response(self, telegram_user: TelegramUser, message: str) -> list[str]:
        # Retry onboarding if it previously failed
        try:
            await self._check_and_handle_onboarding_error(telegram_user)
        except Exception:
            return self._get_error_message_response()

        session_id = self._create_investpal_session_id()

        try:
            ai_response = await self.investpal_client.generate_ai_response(
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

    async def send_reminders_if_due(self):
        reminders = await self.investpal_client.get_agent_reminders(self._create_investpal_user_id())
        if len(reminders) == 0:
            return

        telegram_user = TelegramUser(telegram_id=settings.TELEGRAM_USER_ID, first_name="")
        response_chunks = await self.generate_bot_response(
            telegram_user=telegram_user,
            message="Hello, please give me an update on my reminders",
        )
        for chunk in response_chunks:
            await self.send_adhoc_message(
                telegram_user_id=settings.TELEGRAM_USER_ID,
                message=chunk,
            )

    async def _check_and_handle_onboarding_error(self, telegram_user: TelegramUser):
        if self._onboarded:
            return

        await self._onboard_user_on_investpal(telegram_user)
        self._onboarded = True

    async def _onboard_user_on_investpal(self, telegram_user: TelegramUser):
        investpal_user_id = self._create_investpal_user_id()
        session_id = self._create_investpal_session_id()

        try:
            await self.investpal_client.create_user_context(
                user_id=investpal_user_id,
                user_profile={
                    "first_name": telegram_user.first_name,
                }
            )
        except Exception as e:
            logger.error(f"Failed to create user context: {e}")
            raise e

        try:
            await self.investpal_client.create_session(
                user_id=investpal_user_id,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise e

    async def send_adhoc_message(self, telegram_user_id: str, message: str):
        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=telegram_user_id, text=message, parse_mode="HTML")
            logger.info(f"Message sent successfully to user {telegram_user_id}")
        except TelegramError as e:
            logger.error(f"Failed to send message to user {telegram_user_id}: {e}")
            raise e

    def _create_investpal_user_id(self) -> str:
        if settings.INVESTPAL_USER_ID:
            return settings.INVESTPAL_USER_ID

        return f"telegram:{settings.TELEGRAM_USER_ID}"

    def _create_investpal_session_id(self) -> str:
        return f"telegram_session:{settings.TELEGRAM_USER_ID}"

    def _get_error_message_response(self) -> list[str]:
        return ["I am sorry, something went wrong. Please try again later."]
