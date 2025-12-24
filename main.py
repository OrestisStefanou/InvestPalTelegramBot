import time

from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

from config import settings
from bot_service import BotService
from logger import logger

async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    logger.info(f"User {update.effective_user.id} ({update.effective_user.username}) sent /start")
    bot_service = BotService()
    
    telegram_user_id = str(update.effective_user.id)
    user_first_name = update.effective_user.first_name
    await bot_service.handle_new_user(telegram_user_id, user_first_name)

    bot_response_msgs = await bot_service.generate_bot_response(
        telegram_user_id=telegram_user_id,
        message=f"Hey, I am your new client {user_first_name}!"
    )
    for msg in bot_response_msgs:
        await update.message.reply_text(msg, parse_mode="HTML")
        time.sleep(1)


async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_user_id = str(user.id)
    message_text = update.message.text
    
    # Log the message and user info
    logger.info(f"User {user.id} (@{user.username}) sent: {message_text}")

    bot_service = BotService()
    bot_response_msgs = await bot_service.generate_bot_response(
        telegram_user_id=telegram_user_id,
        message=message_text,
    )
    for msg in bot_response_msgs:
        await update.message.reply_text(msg, parse_mode="HTML")
        time.sleep(1)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", handle_start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message))
    application.add_error_handler(error_handler)
    
    logger.info("Bot is starting with webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=settings.TELEGRAM_WEBHOOK_PORT,
        url_path="webhook",
        webhook_url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
    )

if __name__ == '__main__':
    main()
