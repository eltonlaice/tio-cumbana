import httpx
import pytest
import respx

from app.services.stt import ElevenLabsScribe, STTError


@respx.mock
async def test_http_error_raises_stterror():
    respx.post(ElevenLabsScribe.URL).mock(
        return_value=httpx.Response(401, json={"detail": "invalid key"})
    )
    scribe = ElevenLabsScribe(api_key="bad")
    with pytest.raises(STTError, match="HTTP 401"):
        await scribe.transcribe(b"\x00\x01", "audio/webm")


@respx.mock
async def test_network_error_raises_stterror():
    respx.post(ElevenLabsScribe.URL).mock(side_effect=httpx.ConnectError("boom"))
    scribe = ElevenLabsScribe(api_key="any")
    with pytest.raises(STTError, match="unreachable"):
        await scribe.transcribe(b"\x00\x01", "audio/webm")


@respx.mock
async def test_success_returns_text():
    respx.post(ElevenLabsScribe.URL).mock(
        return_value=httpx.Response(200, json={"text": "  bom dia tio  "})
    )
    scribe = ElevenLabsScribe(api_key="ok")
    text = await scribe.transcribe(b"\x00", "audio/webm")
    assert text == "bom dia tio"


def test_constructor_rejects_empty_key():
    with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
        ElevenLabsScribe(api_key="")
