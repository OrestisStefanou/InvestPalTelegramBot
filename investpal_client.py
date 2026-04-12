import base64
import http

import httpx

from config import settings


class InvestPalClient:
    def __init__(self):
        self._base_url = settings.INVESTPAL_BACKEND_URL

    async def _post(self, path: str, json: dict, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            try:
                return await client.post(f"{self._base_url}{path}", json=json, **kwargs)
            except httpx.RequestError as e:
                raise Exception(f"HTTP POST {path} failed: {e}")

    async def _get(self, path: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            try:
                return await client.get(f"{self._base_url}{path}", **kwargs)
            except httpx.RequestError as e:
                raise Exception(f"HTTP GET {path} failed: {e}")

    async def create_user_context(self, user_id: str, user_profile: dict | None = None):
        response = await self._post(
            "/user_context",
            json={"user_id": user_id, "user_profile": user_profile},
        )
        # http status code conflict means that the user context already exists
        if response.status_code not in [http.HTTPStatus.CREATED, http.HTTPStatus.CONFLICT]:
            raise Exception(f"Failed to create user context with status code: {response.status_code} and text: {response.text}")

    async def create_session(self, user_id: str, session_id: str):
        response = await self._post(
            "/session",
            json={"user_id": user_id, "session_id": session_id},
        )
        # http status code conflict means that the session already exists
        if response.status_code not in [http.HTTPStatus.CREATED, http.HTTPStatus.CONFLICT]:
            raise Exception(f"Failed to create session with status code: {response.status_code} and text: {response.text}")

    async def generate_ai_response(self, session_id: str, message: str) -> str:
        timeout = settings.INVESTPAL_BACKEND_TIMEOUT_MINUTES * 60
        response = await self._post(
            "/chat",
            json={"session_id": session_id, "message": message},
            headers=self._set_up_headers(),
            timeout=timeout,
        )
        if response.status_code != http.HTTPStatus.OK:
            raise Exception(f"Failed to generate AI response with status code: {response.status_code} and text: {response.text}")

        ai_response_msg = response.json().get("response", None)
        if ai_response_msg is None:
            raise Exception("Failed to extract AI response message")

        return ai_response_msg

    async def get_agent_reminders(self, user_id: str) -> list[dict]:
        timeout = settings.INVESTPAL_BACKEND_TIMEOUT_MINUTES * 60
        response = await self._get(
            f"/agent_reminders/{user_id}",
            timeout=timeout,
        )
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
