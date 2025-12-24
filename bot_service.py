from agent_service_client import AgentServiceClient
import utils
from logger import logger

class BotService():
    def __init__(self):
        self.agent_service_client = AgentServiceClient()

    async def handle_new_user(self, telegram_user_id: str, first_name: str):
        user_id = self._create_agent_service_user_id(telegram_user_id)
        session_id = self._create_agent_service_session_id(telegram_user_id)

        try:
            await self.agent_service_client.create_user_context(
                user_id=user_id,
                user_profile={
                    "first_name": first_name,
                }
            )
        except Exception as e:
            logger.error(f"Failed to create user context: {e}")
            raise e

        try:
            await self.agent_service_client.create_session(
                user_id=user_id,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise e

    async def generate_bot_response(self, telegram_user_id: str, message: str) -> list[str]:
        session_id = self._create_agent_service_session_id(telegram_user_id)

        try:
            ai_response = await self.agent_service_client.generate_ai_response(
                session_id=session_id,
                message=message,
            )
        except Exception as e:
            logger.error(f"Failed to generate ai response: {e}")
            return ["I am sorry, something went wrong. Please try again later."]

        response_messages = []
        for msg_chunk in utils.split_ai_response_message(ai_response):
            if msg_chunk == "":
                continue

            telegram_html_msg = utils.markdown_to_telegram_html(msg_chunk)
            if telegram_html_msg == "":
                continue

            response_messages.append(telegram_html_msg)

        return response_messages

    def _create_agent_service_user_id(self, telegram_user_id: str) -> str:
        return f"telegram:{telegram_user_id}"

    def _create_agent_service_session_id(self, telegram_user_id: str) -> str:
        return f"telegram_session:{telegram_user_id}"
