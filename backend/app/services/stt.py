"""Speech-to-text provider abstraction.

Default impl: ElevenLabs Scribe. We do NOT use OpenAI Whisper (hackathon rule:
no non-Anthropic LLM/STT vendors without justification — ElevenLabs is already
the approved voice vendor, so reusing it for STT adds no new dependency).

The Anthropic Messages API does not accept audio content blocks today, so we
must transcribe to text before calling Opus 4.7. This is disclosed in the
README.
"""

from __future__ import annotations

from typing import Protocol

import httpx
import structlog

logger = structlog.get_logger(__name__)


class STTError(RuntimeError):
    """Raised when an STT provider fails to transcribe."""


class STTProvider(Protocol):
    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str: ...


class ElevenLabsScribe:
    """ElevenLabs Scribe STT (https://elevenlabs.io/docs/capabilities/speech-to-text)."""

    URL = "https://api.elevenlabs.io/v1/speech-to-text"

    def __init__(self, api_key: str, model_id: str = "scribe_v1"):
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabsScribe")
        self.api_key = api_key
        self.model_id = model_id

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        headers = {"xi-api-key": self.api_key}
        files = {"file": ("audio", audio_bytes, mime_type)}
        data = {"model_id": self.model_id, "language_code": "por"}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.URL, headers=headers, files=files, data=data)
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("stt.http_error", status=e.response.status_code, body=e.response.text[:200])
            raise STTError(f"ElevenLabs Scribe HTTP {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("stt.network_error", error=str(e))
            raise STTError("ElevenLabs Scribe unreachable") from e
        text = str(payload.get("text", "")).strip()
        logger.info("stt.transcribed", chars=len(text), model=self.model_id)
        return text
