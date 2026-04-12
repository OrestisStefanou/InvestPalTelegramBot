import base64
import http

import httpx

from config import settings


class InvestPalClient:
    def __init__(self):
        pass

    async def create_user_context(self, user_id: str, user_profile: dict | None = None):
        agent_service_url = settings.INVESTPAL_BACKEND_URL
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{agent_service_url}/user_context",
                    json={
                        "user_id": user_id,
                        "user_profile": user_profile,
                    },
                )
            except httpx.RequestError as e:
                raise Exception(f"Failed to create user context: {e}")

            # http status code conflict means that the user context already exists
            if response.status_code not in [http.HTTPStatus.CREATED, http.HTTPStatus.CONFLICT]:
                raise Exception(f"Failed to create user context with status code: {response.status_code} and text: {response.text}")
        
        return

    async def create_session(self, user_id: str, session_id: str):
        agent_service_url = settings.INVESTPAL_BACKEND_URL
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{agent_service_url}/session",
                    json={
                        "user_id": user_id,
                        "session_id": session_id,
                    },
                )
            except httpx.RequestError as e:
                raise Exception(f"Failed to create session: {e}")

            # http status code conflict means that the session already exists
            if response.status_code not in [http.HTTPStatus.CREATED, http.HTTPStatus.CONFLICT]:
                raise Exception(f"Failed to create session with status code: {response.status_code} and text: {response.text}")
        
        return

    async def generate_ai_response(self, session_id: str, message: str) -> str:
        agent_service_url = settings.INVESTPAL_BACKEND_URL
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{agent_service_url}/chat",
                    json={
                        "session_id": session_id,
                        "message": message,
                    },
                    headers=self._set_up_headers(),
                    timeout=settings.INVESTPAL_BACKEND_TIMEOUT_MINUTES * 60,
                )
            except httpx.RequestError as e:
                raise Exception(f"Failed to generate AI response: {e}")

        if response.status_code != http.HTTPStatus.OK:
            raise Exception(f"Failed to generate AI response with status code: {response.status_code} and text: {response.text}")

        ai_response_msg = response.json().get("response", None)

        if ai_response_msg is None:
            raise Exception("Failed to extract AI response message")

        return ai_response_msg

    async def get_agent_reminders(self, user_id: str) -> list[dict]:
        agent_service_url = settings.INVESTPAL_BACKEND_URL
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{agent_service_url}/agent_reminders/{user_id}",
                    timeout=settings.INVESTPAL_BACKEND_TIMEOUT_MINUTES * 60,
                )
            except httpx.RequestError as e:
                raise Exception(f"Failed to get agent reminders: {e}")

        if response.status_code != http.HTTPStatus.OK:
            raise Exception(f"Failed to get agent reminders with status code: {response.status_code} and text: {response.text}")
        
        return response.json()

    def _set_up_headers(self) -> dict[str, any]:
        alpaca_api_key = settings.ALPACA_API_KEY
        alpaca_api_secret = settings.ALPACA_API_SECRET
        coinbase_api_key = settings.COINBASE_API_KEY
        coinbase_api_secret = settings.COINBASE_API_SECRET
        encoded_coinbase_secret = base64.b64encode(
            coinbase_api_secret.encode()
        ).decode()
        
        headers = {}
        if alpaca_api_key and alpaca_api_secret:
            headers["X-Alpaca-Api-Key"] = alpaca_api_key
            headers["X-Alpaca-Api-Secret"] = alpaca_api_secret   

        if coinbase_api_key and coinbase_api_secret:
            headers["X-Coinbase-Api-Key"] = coinbase_api_key
            headers["X-Coinbase-Api-Secret"] = encoded_coinbase_secret

        return headers
