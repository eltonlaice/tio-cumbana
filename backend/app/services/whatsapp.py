"""Twilio WhatsApp Sandbox outbound — proactive voice notes for the demo.

Why Twilio (a second non-Anthropic vendor)?
-------------------------------------------
The product thesis hinges on the farmer's phone *vibrating with a voice
note they didn't ask for*. WhatsApp is where Mozambican smallholders
already live; Telegram has near-zero adoption there. Meta's WhatsApp
Cloud API approval cycle is 5-15 days — well outside the hackathon
window — so we use Twilio's WhatsApp Sandbox, the canonical demo path,
with a shared sandbox number opted into by the demo phone via a `join`
keyword.

Production note: the sandbox is not for production use; once the
project moves past the hackathon we register a real WhatsApp Business
sender. Disclosed in the README.
"""

from __future__ import annotations

from typing import Any

import structlog
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

logger = structlog.get_logger(__name__)


class WhatsAppError(RuntimeError):
    """Raised when the Twilio WhatsApp send fails."""


class TwilioWhatsApp:
    def __init__(self, account_sid: str, auth_token: str, sender: str):
        if not (account_sid and auth_token and sender):
            raise ValueError("TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM are required")
        self.client = Client(account_sid, auth_token)
        # Accept either "whatsapp:+14155238886" or just "+14155238886" — normalise.
        self.sender = sender if sender.startswith("whatsapp:") else f"whatsapp:{sender}"

    def send_voice_note(self, to: str, body: str, media_url: str | None = None) -> str:
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        params: dict[str, Any] = {"from_": self.sender, "to": to, "body": body}
        if media_url:
            params["media_url"] = [media_url]
        try:
            msg = self.client.messages.create(**params)
        except TwilioException as e:
            logger.error("whatsapp.send_failed", error=str(e), to=to)
            raise WhatsAppError(f"Twilio send failed: {e}") from e
        logger.info("whatsapp.sent", sid=msg.sid, to=to, has_media=bool(media_url))
        return str(msg.sid)
