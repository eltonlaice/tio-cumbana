"""Tiny in-memory cache for audio blobs that need a short-lived public URL.

Used to expose ElevenLabs-synthesised voice notes as a `media_url` to
Twilio (which fetches the URL when forwarding the WhatsApp message).
A real deployment would push to S3 with a presigned URL; for the demo,
serving directly from App Runner is fine — volume is tiny and the
TTL (10 min) keeps memory bounded.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

_cache: dict[str, tuple[bytes, str, datetime]] = {}
_TTL = timedelta(minutes=10)


def store(audio: bytes, mime: str = "audio/mpeg") -> str:
    audio_id = secrets.token_urlsafe(16)
    _cache[audio_id] = (audio, mime, datetime.now(timezone.utc))
    _cleanup()
    return audio_id


def get(audio_id: str) -> tuple[bytes, str] | None:
    item = _cache.get(audio_id)
    if item is None:
        return None
    bytes_, mime, _ = item
    return bytes_, mime


def _cleanup() -> None:
    now = datetime.now(timezone.utc)
    expired = [k for k, v in _cache.items() if now - v[2] > _TTL]
    for k in expired:
        del _cache[k]
