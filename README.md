# Telegram Investor Bot

A Telegram-based user interface for interacting with the [InvestPal](https://github.com/OrestisStefanou/InvestPal) backend — a personal AI-powered investment assistant.

## Features

- **Personalized Investment Assistance**: Interacts with users to provide investment-related information and advice.
- **Single-User Access Control**: Restricts the bot to a specific Telegram user ID — all other users receive an "Unauthorized" response.
- **Session Management**: Maintains user context and sessions across interactions.
- **AI Integration**: Leverages the [InvestPal Agent Service](https://github.com/OrestisStefanou/InvestPal) for generating intelligent responses.
- **Trading Account Integration**: Optionally passes Alpaca and Coinbase API credentials to the agent service so the AI can access your brokerage accounts.
- **Message Formatting**: Automatically transforms AI-generated markdown into Telegram-compatible HTML.
- **Agent Reminders**: A standalone workflow (`workflows/agent_reminders.py`) that can be run on a schedule to check for pending AI reminders and deliver them to the user.
- **Asynchronous & Robust**: Built using `python-telegram-bot` with a focus on reliability and performance.

## Prerequisites

- Python >= 3.14
- [uv](https://github.com/astral-sh/uv) (recommended for package management)
- Access to a running instance of the [InvestPal Agent Service](https://github.com/OrestisStefanou/InvestPal).

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd telegram_bot
    ```

2.  **Install dependencies**:
    Using `uv`:
    ```bash
    uv sync
    ```

3.  **Configure environment variables**:
    Create a `.env` file in the project directory:

    **Required:**
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    TELEGRAM_WEBHOOK_URL=your_webhook_base_url
    TELEGRAM_WEBHOOK_PORT=8080
    TELEGRAM_USER_ID=your_telegram_user_id
    INVESTPAL_BACKEND_URL=http://localhost:8000
    ```

    **Optional:**
    ```env
    # Timeout for requests to the InvestPal agent service (default: 5 minutes)
    INVESTPAL_BACKEND_TIMEOUT_MINUTES=5

    # Use an existing InvestPal user ID instead of creating one based on your Telegram ID
    INVESTPAL_USER_ID=

    # Alpaca brokerage credentials — forwarded to the agent service for account access
    ALPACA_API_KEY=
    ALPACA_API_SECRET=

    # Coinbase credentials — forwarded to the agent service for account access
    COINBASE_API_KEY=
    COINBASE_API_SECRET=
    ```

    > **How to find your Telegram user ID**: Send a message to [@userinfobot](https://t.me/userinfobot) on Telegram.

## Running the Bot

To start the bot using `uv`:
```bash
uv run main.py
```

The bot starts in webhook mode. Ensure your `TELEGRAM_WEBHOOK_URL` is accessible by Telegram's servers (e.g., via `ngrok` for local development).

## Architecture

This project is part of the **InvestPal** ecosystem. It serves as the frontend (Telegram interface) while the core logic and AI reasoning are handled by the [InvestPal Agent Service](https://github.com/OrestisStefanou/InvestPal).


## Project Structure

- `main.py`: Entry point for the Telegram bot — registers handlers and runs the webhook server.
- `bot_service.py`: Core business logic — onboarding, response generation, and the reminders workflow.
- `investpal_client.py`: HTTP client for communicating with the InvestPal agent service.
- `config.py`: Configuration management using Pydantic Settings.
- `utils.py`: Utility functions for message splitting and markdown-to-HTML formatting.
- `logger.py`: Application logging setup.
- `workflows/agent_reminders.py`: Standalone script that checks for pending AI reminders and sends them to the user. Intended to be run on a schedule (e.g., via cron).

## Development

Currently, the bot uses webhooks for receiving updates. For local development, you might want to use a tool like `ngrok` to expose your local port to the internet.

```bash
ngrok http 8080
```
Then update your `.env` with the provided ngrok URL.