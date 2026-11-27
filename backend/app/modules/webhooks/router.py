from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from app.modules.webhooks.service import FBWebhookService

router = APIRouter()


@router.get("/webhook", response_class=PlainTextResponse)
def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    return FBWebhookService.handshake(mode, token, challenge)


@router.post("/webhook")
async def receive(request: Request):
    body = await request.body()
    return FBWebhookService.receive_data(body, request.headers.get("X-Hub-Signature-256"))