import pytest

from app.models.schemas import FarmerProfile
from app.services.farmer_context import load_farmer, render_context_block


@pytest.mark.asyncio
async def test_known_farmer_loads_full_profile():
    farmer = await load_farmer("+258840000001")
    assert farmer.name == "Dona Maria"
    assert "pepino (Epsilon F1)" in farmer.crops
    assert any("Mancozeb" in p for p in farmer.preferences)


@pytest.mark.asyncio
async def test_unknown_farmer_returns_generic_profile():
    farmer = await load_farmer("+258849999999")
    assert farmer.name == "Agricultor"
    assert farmer.crops == []
    assert farmer.language_mix == "pt-dominant"


def test_render_context_block_includes_preferences_and_history():
    farmer = FarmerProfile(
        phone="+258840000001",
        name="Dona Maria",
        location="Maluana",
        crops=["pepino"],
        soil="arenoso",
        preferences=["não usa Mancozeb"],
        history=["semana 2: rega excessiva corrigida"],
        language_mix="mixed",
    )
    block = render_context_block(farmer)
    assert "Dona Maria" in block
    assert "Maluana" in block
    assert "não usa Mancozeb" in block
    assert "semana 2" in block
    assert "mixed" in block


def test_render_context_block_omits_empty_sections():
    farmer = FarmerProfile(
        phone="+258840000999",
        name="Anon",
        location="Moçambique",
        crops=[],
    )
    block = render_context_block(farmer)
    assert "Culturas:" not in block
    assert "Preferências:" not in block
    assert "Histórico" not in block
