from datetime import datetime, timezone

import pytest

from app.models.schemas import MarketPriceUpdate
from app.services import market_prices as svc


@pytest.mark.asyncio
async def test_seed_pool_has_known_crops():
    snaps = await svc.all_snapshots()
    crops = {s.crop for s in snaps}
    assert {"pepino", "tomate", "cebola", "alho", "pimento"}.issubset(crops)


@pytest.mark.asyncio
async def test_snapshot_returns_latest_first():
    snap = await svc.snapshot("pepino")
    assert snap.sample_size_7d >= 3
    assert snap.contributors_7d >= 2
    assert snap.latest_wholesale is not None
    assert snap.median_wholesale_7d is not None


@pytest.mark.asyncio
async def test_snapshot_unknown_crop_is_empty():
    snap = await svc.snapshot("manioca-roxa-de-marte")
    assert snap.sample_size_7d == 0
    assert snap.latest_wholesale is None
    assert snap.contributors_7d == 0


@pytest.mark.asyncio
async def test_add_observation_appears_in_snapshot():
    initial = await svc.snapshot("couve")
    assert initial.sample_size_7d == 0  # not in seed
    await svc.add_observation(
        MarketPriceUpdate(
            contributor_phone="+258840000099",
            crop="couve",
            price_wholesale=15,
            price_retail=25,
            observed_at=datetime.now(timezone.utc),
        )
    )
    after = await svc.snapshot("couve")
    assert after.sample_size_7d == 1
    assert after.latest_wholesale == 15
