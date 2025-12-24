# Telegram Investor Bot

A Telegram bot that acts as a personal investor assistant, powered by an underlying AI agent service.

## Features

- **Personalized Investment Assistance**: Interacts with users to provide investment-related information and advice.
- **Session Management**: Maintains user context and sessions across interactions.
- **AI Integration**: Leverages a separate agent service for generating intelligent responses.
- **Message Formatting**: Automatically transforms AI-generated markdown into Telegram-compatible HTML.
- **Asynchronous & Robust**: Built using `python-telegram-bot` with a focus on reliability and performance.

## Prerequisites

- Python >= 3.14
- [uv](https://github.com/astral-sh/uv) (recommended for package management)
- Access to a running instance of the `agent_service`.

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
    Create a `.env` file in the `telegram_bot` directory:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    TELEGRAM_WEBHOOK_URL=your_webhook_base_url
    TELEGRAM_WEBHOOK_PORT=8080
    AGENT_SERVICE_URL=http://localhost:8000
    ```

## Running the Bot

To start the bot using `uv`:
```bash
uv run main.py
```

The bot starts in webhook mode. Ensure your `TELEGRAM_WEBHOOK_URL` is accessible by Telegram's servers (e.g., via `ngrok` for local development).

## Project Structure

- `main.py`: The entry point for the Telegram bot, handles commands and messages.
- `bot_service.py`: Contains the core logic for interacting with the agent service and processing responses.
- `agent_service_client.py`: An HTTP client for communicating with the AI agent service.
- `config.py`: Handles configuration management using Pydantic Settings.
- `utils.py`: Utility functions for message splitting and formatting.
- `logger.py`: Configures application logging.

## Development

Currently, the bot uses webhooks for receiving updates. For local development, you might want to use a tool like `ngrok` to expose your local port to the internet.

```bash
ngrok http 8080
```
Then update your `.env` with the provided ngrok URL.