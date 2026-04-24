"""Opus 4.7 multimodal client.

Composes a single Messages API call with:
  - system prompt: Tio Cumbana persona
  - user content: image block (plant photo) + text block (farmer context + voice transcript)

Audio is NOT sent as a content block because the Anthropic Messages API does
not currently accept audio input (verified Apr 2026 — see docs/architecture.md).
Audio is transcribed upstream by `services/stt.py`.
"""

from __future__ import annotations

import base64
from typing import Any

import structlog
from anthropic import AsyncAnthropic

from app.models.schemas import FarmerProfile
from app.prompts.tio_cumbana import build_system_prompt
from app.services.farmer_context import render_context_block

logger = structlog.get_logger(__name__)


class TioCumbanaLLM:
    def __init__(self, api_key: str, model: str = "claude-opus-4-7"):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def consult(
        self,
        *,
        farmer: FarmerProfile,
        photo_bytes: bytes,
        photo_mime: str,
        voice_transcript: str,
    ) -> str:
        context = render_context_block(farmer)
        user_text = (
            f"--- Contexto do agricultor ---\n{context}\n\n"
            f"--- Nota de voz (transcrita) ---\n{voice_transcript or '(sem áudio)'}\n\n"
            f"Foto anexa. Responde como Tio Cumbana."
        )
        content: list[dict[str, Any]] = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": photo_mime,
                    "data": base64.b64encode(photo_bytes).decode(),
                },
            },
            {"type": "text", "text": user_text},
        ]

        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=build_system_prompt(),
            messages=[{"role": "user", "content": content}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text").strip()
        logger.info(
            "llm.consult",
            model=self.model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            farmer=farmer.phone,
        )
        return text

    async def proactive(self, *, farmer: FarmerProfile, trigger: str) -> str:
        """Generate an unprompted outbound message from Tio Cumbana."""
        context = render_context_block(farmer)
        user_text = (
            f"--- Contexto do agricultor ---\n{context}\n\n"
            f"--- Gatilho proactivo ---\n{trigger}\n\n"
            "Abre a mensagem directamente com o facto (sem 'Olá'). "
            "Dá o próximo passo concreto."
        )
        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=build_system_prompt(),
            messages=[{"role": "user", "content": user_text}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text").strip()
        logger.info(
            "llm.proactive",
            model=self.model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            farmer=farmer.phone,
            trigger=trigger,
        )
        return text
