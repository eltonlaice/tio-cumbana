from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services import audio_cache

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/{audio_id}")
async def get_audio(audio_id: str) -> Response:
    item = audio_cache.get(audio_id)
    if item is None:
        raise HTTPException(status_code=404, detail="audio expired or not found")
    audio, mime = item
    return Response(content=audio, media_type=mime)
