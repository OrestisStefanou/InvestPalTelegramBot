"""
Agent reminders workflow.

Entry point for checking and dispatching agent reminders. Initialises the
BotService and checks whether any agent reminders are due. If reminders
exist, the bot generates an update message and sends it to the configured
Telegram user as an ad-hoc message.
"""
import asyncio

from bot_service import BotService


async def main():
    bot_service = BotService()
    await bot_service.send_reminders_if_due()


if __name__ == "__main__":
    asyncio.run(main())
