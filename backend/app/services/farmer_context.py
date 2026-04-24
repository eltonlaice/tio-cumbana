"""Farmer profile loader.

For the hackathon demo, profiles are hardcoded in-memory. Moving to Supabase
is a drop-in swap: implement `load_from_supabase` and flip the call site.
"""

from __future__ import annotations

from app.models.schemas import FarmerProfile

_HARDCODED: dict[str, FarmerProfile] = {
    "+258840000001": FarmerProfile(
        phone="+258840000001",
        name="Dona Maria",
        location="Maluana, Marracuene",
        crops=["pepino (Epsilon F1)", "pimento (Indra F1)"],
        planting_dates={"pepino": "2026-03-15", "pimento": "2026-03-22"},
        soil="arenoso, drena rápido",
        preferences=[
            "não gosta de Mancozeb",
            "rega só de manhã, nunca à tarde",
        ],
        history=[
            "semana 2: relatou manchas amarelas nas folhas de baixo do pepino — diagnóstico: rega excessiva, corrigido",
            "semana 3: perguntou sobre preço de pepino em Zimpeto",
        ],
        language_mix="mixed",
    ),
    "+258840000002": FarmerProfile(
        phone="+258840000002",
        name="Tio Armando",
        location="Marracuene-sede",
        crops=["batata-semente", "couve"],
        planting_dates={"batata": "2026-02-28"},
        soil="argiloso, retém humidade",
        preferences=["compra sempre em AQI Machava"],
        history=[],
        language_mix="pt-dominant",
    ),
    "+258840000003": FarmerProfile(
        phone="+258840000003",
        name="Mana Celeste",
        location="Bobole, Marracuene",
        crops=["tomate", "feijão-nhemba"],
        planting_dates={"tomate": "2026-03-01"},
        soil="arenoso-franco",
        preferences=[],
        history=["semana 1: perguntou sobre espaçamento do tomate"],
        language_mix="changana-dominant",
    ),
}


async def load_farmer(phone: str) -> FarmerProfile:
    """Return farmer by phone number. Falls back to a generic unknown profile."""
    if phone in _HARDCODED:
        return _HARDCODED[phone]
    return FarmerProfile(
        phone=phone,
        name="Agricultor",
        location="Moçambique",
        crops=[],
        soil="",
        preferences=[],
        history=[],
        language_mix="pt-dominant",
    )


def render_context_block(farmer: FarmerProfile) -> str:
    """Serialise the farmer profile as a plain-text block for the user message."""
    lines = [
        f"Agricultor: {farmer.name}",
        f"Localização: {farmer.location}",
    ]
    if farmer.crops:
        lines.append("Culturas: " + ", ".join(farmer.crops))
    if farmer.planting_dates:
        pd = ", ".join(f"{k} em {v}" for k, v in farmer.planting_dates.items())
        lines.append(f"Plantios: {pd}")
    if farmer.soil:
        lines.append(f"Solo: {farmer.soil}")
    if farmer.preferences:
        lines.append("Preferências: " + "; ".join(farmer.preferences))
    if farmer.history:
        lines.append("Histórico recente:")
        for h in farmer.history:
            lines.append(f"  - {h}")
    lines.append(f"Registo linguístico: {farmer.language_mix}")
    return "\n".join(lines)
