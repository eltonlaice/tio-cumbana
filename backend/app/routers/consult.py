from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
import structlog

from app.config import Settings, get_settings
from app.models.schemas import (
    ConsultResponse,
    ProactiveRequest,
    ProactiveResponse,
)
from anthropic import AsyncAnthropic

from app.services import audio_cache
from app.services.anthropic_client import TioCumbanaLLM
from app.services.farmer_context import load_farmer
from app.services.managed_agent import TioCumbanaManagedAgent
from app.services.stt import ElevenLabsScribe
from app.services.tts import ElevenLabsTTS, TTSError
from app.services.whatsapp import TwilioWhatsApp, WhatsAppError

router = APIRouter(prefix="/api", tags=["consult"])
log = structlog.get_logger(__name__)


def _llm(settings: Settings) -> TioCumbanaLLM:
    return TioCumbanaLLM(api_key=settings.anthropic_api_key, model=settings.claude_model)


def _stt(settings: Settings) -> ElevenLabsScribe:
    return ElevenLabsScribe(api_key=settings.elevenlabs_api_key)


def _tts(settings: Settings) -> ElevenLabsTTS:
    return ElevenLabsTTS(
        api_key=settings.elevenlabs_api_key, voice_id=settings.elevenlabs_voice_id
    )


@router.post("/consult", response_model=ConsultResponse)
async def consult(
    photo: UploadFile = File(...),
    audio: UploadFile = File(...),
    farmer_phone: str = Form(...),
    settings: Settings = Depends(get_settings),
) -> ConsultResponse:
    photo_bytes = await photo.read()
    audio_bytes = await audio.read()
    if not photo_bytes or not audio_bytes:
        raise HTTPException(status_code=400, detail="photo and audio are required")

    farmer = await load_farmer(farmer_phone)

    transcript = await _stt(settings).transcribe(
        audio_bytes, audio.content_type or "audio/webm"
    )

    text = await _llm(settings).consult(
        farmer=farmer,
        photo_bytes=photo_bytes,
        photo_mime=photo.content_type or "image/jpeg",
        voice_transcript=transcript,
    )

    audio_b64: str | None = None
    if settings.elevenlabs_voice_id:
        try:
            audio_bytes_out, _mime = await _tts(settings).synthesize(text)
            audio_b64 = base64.b64encode(audio_bytes_out).decode()
        except TTSError as e:
            log.warning("consult.tts_skipped", error=str(e))
    else:
        log.warning("tts.skipped", reason="ELEVENLABS_VOICE_ID not set")

    return ConsultResponse(text=text, audio_b64=audio_b64, farmer=farmer)


@router.post("/proactive", response_model=ProactiveResponse)
async def proactive(
    req: ProactiveRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> ProactiveResponse:
    farmer = await load_farmer(req.farmer_phone)

    if settings.use_managed_agent and settings.managed_agent_id:
        # Production path: a long-running Managed Agent decides whether to
        # interrupt and what to say. See services/managed_agent.py.
        ma_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        ma = TioCumbanaManagedAgent(
            ma_client,
            settings.managed_agent_id,
            settings.managed_environment_id,
        )
        snapshot = {"trigger": req.trigger}  # real impl: weather, prices, photo URLs
        decision = await ma.tick(farmer, snapshot)
        if decision.action != "message" or not decision.content:
            return ProactiveResponse(
                text=f"(no_action: {decision.reason or 'silent'})",
                farmer=farmer,
                trigger=req.trigger,
            )
        text = decision.content
    else:
        # Demo path (default): scripted single-shot generation.
        text = await _llm(settings).proactive(farmer=farmer, trigger=req.trigger)

    audio_b64: str | None = None
    audio_bytes_out: bytes | None = None
    audio_mime = "audio/mpeg"
    if settings.elevenlabs_voice_id:
        try:
            audio_bytes_out, audio_mime = await _tts(settings).synthesize(text)
            audio_b64 = base64.b64encode(audio_bytes_out).decode()
        except TTSError as e:
            log.warning("proactive.tts_skipped", error=str(e))

    # Send via WhatsApp if Twilio is configured. The voice note is hosted
    # on this same backend at /api/audio/<id> with a 10-min TTL, so Twilio
    # can fetch it as the message media.
    if (
        audio_bytes_out
        and settings.twilio_account_sid
        and settings.twilio_auth_token
        and settings.twilio_whatsapp_from
        and settings.mother_whatsapp_to
    ):
        try:
            audio_id = audio_cache.store(audio_bytes_out, audio_mime)
            base_url = str(request.base_url).rstrip("/")
            media_url = f"{base_url}/api/audio/{audio_id}"
            wa = TwilioWhatsApp(
                settings.twilio_account_sid,
                settings.twilio_auth_token,
                settings.twilio_whatsapp_from,
            )
            wa.send_voice_note(
                to=settings.mother_whatsapp_to,
                body=text,
                media_url=media_url,
            )
            log.info("proactive.whatsapp_sent", to=settings.mother_whatsapp_to)
        except WhatsAppError as e:
            # Don't fail the API call if WhatsApp delivery breaks; the
            # frontend already has audio_b64 to play.
            log.warning("proactive.whatsapp_skipped", error=str(e))

    return ProactiveResponse(text=text, audio_b64=audio_b64, farmer=farmer, trigger=req.trigger)
