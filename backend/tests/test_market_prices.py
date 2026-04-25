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
async def test_snapshot_confirmed_with_quorum():
    snap = await svc.snapshot("pepino")
    assert snap.contributors_24h >= 2
    assert snap.confirmed is True
    assert snap.median_wholesale is not None
    assert snap.min_wholesale is not None
    assert snap.max_wholesale is not None
    assert snap.min_wholesale <= snap.median_wholesale <= snap.max_wholesale


@pytest.mark.asyncio
async def test_snapshot_unknown_crop_is_empty():
    snap = await svc.snapshot("manioca-roxa-de-marte")
    assert snap.sample_size_24h == 0
    assert snap.confirmed is False
    assert snap.median_wholesale is None
    assert snap.contributors_24h == 0


@pytest.mark.asyncio
async def test_single_contribution_is_unconfirmed():
    initial = await svc.snapshot("couve")
    assert initial.sample_size_24h == 0
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
    assert after.sample_size_24h == 1
    assert after.contributors_24h == 1
    assert after.confirmed is False  # quorum not met


@pytest.mark.asyncio
async def test_two_distinct_contributors_confirms():
    await svc.add_observation(
        MarketPriceUpdate(
            contributor_phone="+258840000091",
            crop="abóbora",
            price_wholesale=20,
            observed_at=datetime.now(timezone.utc),
        )
    )
    snap1 = await svc.snapshot("abóbora")
    assert snap1.confirmed is False
    await svc.add_observation(
        MarketPriceUpdate(
            contributor_phone="+258840000092",
            crop="abóbora",
            price_wholesale=22,
            observed_at=datetime.now(timezone.utc),
        )
    )
    snap2 = await svc.snapshot("abóbora")
    assert snap2.confirmed is True
    assert snap2.min_wholesale == 20
    assert snap2.max_wholesale == 22
