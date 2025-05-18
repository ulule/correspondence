from typing import Any, Optional

import httpx
from fastapi import status
from pydantic import BaseModel, Field


class Provider:
    def __init__(self, **kw: Any) -> None:
        pass

    async def create_message(self, from_: str, to: str, body: str) -> list[str] | None:
        raise NotImplementedError


class NoopProvider(Provider):
    async def create_message(self, from_: str, to: str, body: str) -> list[str] | None:
        return None


class NexmoMessageResponse(BaseModel):
    to: Optional[str] = None
    message_id: Optional[str] = Field(None, validation_alias="message-id")
    status: Optional[str] = None
    remaining_balance: Optional[str] = Field(None, validation_alias="remaining-balance")
    message_price: Optional[str] = Field(None, validation_alias="message-price")
    network: Optional[str] = None
    client_ref: Optional[str] = Field(None, validation_alias="client-ref")
    account_ref: Optional[str] = Field(None, validation_alias="account-ref")


class NexmoSmsResponse(BaseModel):
    message_count: str = Field(..., validation_alias="message-count")
    messages: list[NexmoMessageResponse]


class NexmoProvider(Provider):
    account: str
    token: str
    client: httpx.AsyncClient
    base_url = "https://rest.nexmo.com"

    def __init__(self, account: str, token: str):
        self.account = account
        self.token = token
        self.client = httpx.AsyncClient()

    async def post(self, path: str, payload: dict[str, Any]) -> httpx.Response:
        payload.update(
            {
                "api_key": self.account,
                "api_secret": self.token,
            }
        )

        return await self.client.post(f"{self.base_url}{path}", json=payload)

    async def create_message(self, from_: str, to: str, body: str) -> list[str] | None:
        response = await self.post(
            "/sms/json",
            {
                "from": from_,
                "to": to,
                "text": body,
                "type": "unicode",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        sms_response = NexmoSmsResponse(**body)  # type: ignore

        return [
            message.message_id
            for message in sms_response.messages
            if message.message_id
        ]
