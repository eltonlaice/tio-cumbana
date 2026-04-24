"""Text-to-speech provider abstraction.

Default impl: ElevenLabs (cloned voice). The voice cloning piece is the only
approved non-Anthropic dependency — Anthropic does not offer voice cloning,
and the cloned voice IS the product identity.

If the hackathon rule interpretation forces a pivot away from ElevenLabs,
swap this module for an OSS backend (F5-TTS, OpenVoice, Piper) without
touching the router.
"""

from __future__ import annotations

from typing import Protocol

import httpx
import structlog

logger = structlog.get_logger(__name__)


class TTSProvider(Protocol):
    async def synthesize(self, text: str) -> tuple[bytes, str]:
        """Return (audio_bytes, mime_type)."""
        ...


class ElevenLabsTTS:
    """ElevenLabs TTS with a cloned voice.

    Docs: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
    """

    BASE = "https://api.elevenlabs.io/v1/text-to-speech"

    def __init__(self, api_key: str, voice_id: str, model_id: str = "eleven_multilingual_v2"):
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabsTTS")
        if not voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID is required for ElevenLabsTTS")
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id

    async def synthesize(self, text: str) -> tuple[bytes, str]:
        url = f"{self.BASE}/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        body = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.85},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            audio = resp.content
        logger.info("tts.synthesized", bytes=len(audio), voice=self.voice_id)
        return audio, "audio/mpeg"
