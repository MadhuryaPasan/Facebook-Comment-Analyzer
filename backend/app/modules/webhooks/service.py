import hashlib
import hmac
import json

from fastapi import HTTPException

from app.core.config import Config


class FBWebhookService:

    @staticmethod
    def handshake(mode: str = "", token: str = "", challenge: str = ""):
        if (
            mode == "subscribe"
            and token
            and hmac.compare_digest(token.encode(), Config.FB_VERIFY_TOKEN.encode())
        ):
            return challenge
        raise HTTPException(status_code=403)

    @staticmethod
    def receive_data(body: bytes, signature: str | None):
        expected = "sha256=" + hmac.new(Config.FB_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()

        if not signature or not hmac.compare_digest(signature.encode(), expected.encode()):
            raise HTTPException(status_code=401)

        payload = json.loads(body)
        print(json.dumps(payload, indent=2))
        return {"status": "ok"}