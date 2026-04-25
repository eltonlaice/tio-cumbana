import httpx
import pytest
import respx

from app.services.tts import ElevenLabsTTS, TTSError

VOICE = "voice_123"
URL = f"{ElevenLabsTTS.BASE}/{VOICE}"


@respx.mock
async def test_http_error_raises_ttserror():
    respx.post(URL).mock(return_value=httpx.Response(429, text="rate limit"))
    tts = ElevenLabsTTS(api_key="ok", voice_id=VOICE)
    with pytest.raises(TTSError, match="HTTP 429"):
        await tts.synthesize("olá")


@respx.mock
async def test_network_error_raises_ttserror():
    respx.post(URL).mock(side_effect=httpx.ConnectError("boom"))
    tts = ElevenLabsTTS(api_key="ok", voice_id=VOICE)
    with pytest.raises(TTSError, match="unreachable"):
        await tts.synthesize("olá")


@respx.mock
async def test_success_returns_audio_bytes_and_mime():
    audio_bytes = b"\x49\x44\x33\x04"
    respx.post(URL).mock(return_value=httpx.Response(200, content=audio_bytes))
    tts = ElevenLabsTTS(api_key="ok", voice_id=VOICE)
    audio, mime = await tts.synthesize("olá")
    assert audio == audio_bytes
    assert mime == "audio/mpeg"


def test_constructor_rejects_empty_voice_id():
    with pytest.raises(ValueError, match="ELEVENLABS_VOICE_ID"):
        ElevenLabsTTS(api_key="ok", voice_id="")
