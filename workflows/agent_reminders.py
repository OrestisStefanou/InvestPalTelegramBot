import asyncio

from bot_service import BotService, TelegramUser
from config import settings

async def main():
    bot_service = BotService()

    # first check if agent has any reminders for this user
    investpal_user_id = bot_service._create_investpal_user_id(settings.TELEGRAM_USER_ID)
    reminders = await bot_service.investpal_client.get_agent_reminders(investpal_user_id)

    if len(reminders) == 0:
        return

    # Ask agent to check user reminders
    user_id = settings.TELEGRAM_USER_ID
    if settings.INVESTPAL_USER_ID:
        user_id = settings.INVESTPAL_USER_ID
    
    agent_response_msg_chunks = await bot_service.generate_bot_response(
        telegram_user=TelegramUser(
            user_id=user_id,
            first_name="",
        ),
        message="Hello, please give me an update on my reminders"
    )

    for chuck in agent_response_msg_chunks:
        await bot_service.send_adhoc_message(
            telegram_user_id=settings.TELEGRAM_USER_ID,
            message=chuck,
        )


if __name__ == "__main__":
    asyncio.run(main())