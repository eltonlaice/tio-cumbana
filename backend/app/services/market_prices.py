"""Community-sourced market price pool — Zimpeto wholesale + retail.

The thesis
----------
Mozambique has no public real-time API for wholesale agricultural prices.
SIMA Moç publishes a weekly PDF; INE aggregates monthly. Smallholders
trade rumour over WhatsApp. Tio Cumbana flips the scarcity into a
network effect: each farmer who walks to Zimpeto contributes the
prices they saw, and the agent serves the aggregated view back to the
next farmer who's about to leave home.

This is a fourth innovation layered on top of the three in CLAUDE.md
§6 — "agronomy is relational" extended from messaging to data.

For the hackathon demo, the store is in-memory with a seed of plausible
April-2026 prices contributed by three named farmers (the same ones
already in `farmer_context.py`). Production: persist to Supabase, add
spam moderation, add geo-keyed markets beyond Zimpeto.
"""

from __future__ import annotations

import statistics
from datetime import datetime, timedelta, timezone

from app.models.schemas import MarketPriceSnapshot, MarketPriceUpdate

_now = datetime.now(timezone.utc)


def _h(hours: float) -> datetime:
    return _now - timedelta(hours=hours)


# Seed pool — 3 contributors × 5 crops over the last ~30 hours.
# Values are placeholders calibrated to plausible Zimpeto ranges (Apr 2026).
# Replace with real observations once the network has its first week of data.
_pool: list[MarketPriceUpdate] = [
    # Pepino (cucumber)
    MarketPriceUpdate(
        contributor_phone="+258840000001", crop="pepino",
        price_wholesale=55, price_retail=95, observed_at=_h(28),
        note="abundant supply this week",
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000002", crop="pepino",
        price_wholesale=60, price_retail=100, observed_at=_h(20),
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000003", crop="pepino",
        price_wholesale=65, price_retail=110, observed_at=_h(4),
        note="prices firming up — fewer trucks today",
    ),
    # Pimento (bell pepper)
    MarketPriceUpdate(
        contributor_phone="+258840000001", crop="pimento",
        price_wholesale=85, price_retail=140, observed_at=_h(28),
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000002", crop="pimento",
        price_wholesale=95, price_retail=150, observed_at=_h(6),
    ),
    # Tomate
    MarketPriceUpdate(
        contributor_phone="+258840000003", crop="tomate",
        price_wholesale=70, price_retail=110, observed_at=_h(26),
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000001", crop="tomate",
        price_wholesale=75, price_retail=120, observed_at=_h(5),
    ),
    # Cebola (onion)
    MarketPriceUpdate(
        contributor_phone="+258840000002", crop="cebola",
        price_wholesale=40, price_retail=70, observed_at=_h(24),
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000001", crop="cebola",
        price_wholesale=42, price_retail=72, observed_at=_h(8),
    ),
    # Alho (garlic)
    MarketPriceUpdate(
        contributor_phone="+258840000002", crop="alho",
        price_wholesale=240, price_retail=400, observed_at=_h(23),
        note="imported from South Africa",
    ),
    MarketPriceUpdate(
        contributor_phone="+258840000003", crop="alho",
        price_wholesale=260, price_retail=420, observed_at=_h(7),
    ),
]


async def add_observation(update: MarketPriceUpdate) -> None:
    _pool.append(update)


async def list_recent(limit: int = 20) -> list[MarketPriceUpdate]:
    return sorted(_pool, key=lambda u: u.observed_at, reverse=True)[:limit]


CONFIRMATION_QUORUM = 2  # distinct contributors required in window


async def snapshot(crop: str, market: str = "Zimpeto") -> MarketPriceSnapshot:
    crop = crop.lower().strip()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    rows = [u for u in _pool if u.crop == crop and u.market == market and u.observed_at >= cutoff]
    rows.sort(key=lambda u: u.observed_at, reverse=True)

    if not rows:
        return MarketPriceSnapshot(
            crop=crop,
            market=market,
            confirmed=False,
            median_wholesale=None,
            median_retail=None,
            min_wholesale=None,
            max_wholesale=None,
            min_retail=None,
            max_retail=None,
            contributors_24h=0,
            sample_size_24h=0,
            last_observed_at=None,
        )

    ws = [u.price_wholesale for u in rows if u.price_wholesale is not None]
    rs = [u.price_retail for u in rows if u.price_retail is not None]
    contributors = {u.contributor_phone for u in rows}
    return MarketPriceSnapshot(
        crop=crop,
        market=market,
        confirmed=len(contributors) >= CONFIRMATION_QUORUM,
        median_wholesale=statistics.median(ws) if ws else None,
        median_retail=statistics.median(rs) if rs else None,
        min_wholesale=min(ws) if ws else None,
        max_wholesale=max(ws) if ws else None,
        min_retail=min(rs) if rs else None,
        max_retail=max(rs) if rs else None,
        contributors_24h=len(contributors),
        sample_size_24h=len(rows),
        last_observed_at=rows[0].observed_at,
    )


async def all_snapshots(market: str = "Zimpeto") -> list[MarketPriceSnapshot]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    crops = sorted(
        {u.crop for u in _pool if u.market == market and u.observed_at >= cutoff}
    )
    return [await snapshot(c, market) for c in crops]
