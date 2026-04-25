from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.schemas import MarketPriceSnapshot, MarketPriceUpdate
from app.services import market_prices as svc

router = APIRouter(prefix="/api/market-prices", tags=["market"])


@router.get("", response_model=list[MarketPriceSnapshot])
async def get_all() -> list[MarketPriceSnapshot]:
    """Aggregated price snapshot per crop, all markets default to Zimpeto."""
    return await svc.all_snapshots()


@router.get("/{crop}", response_model=MarketPriceSnapshot)
async def get_one(crop: str) -> MarketPriceSnapshot:
    snap = await svc.snapshot(crop)
    if snap.sample_size_7d == 0:
        raise HTTPException(status_code=404, detail=f"no price data for {crop}")
    return snap


@router.get("/recent/list", response_model=list[MarketPriceUpdate])
async def get_recent(limit: int = 20) -> list[MarketPriceUpdate]:
    return await svc.list_recent(limit=limit)


@router.post("", response_model=MarketPriceUpdate, status_code=201)
async def contribute(body: MarketPriceUpdate) -> MarketPriceUpdate:
    if body.price_wholesale is None and body.price_retail is None:
        raise HTTPException(
            status_code=400, detail="at least one of price_wholesale or price_retail is required"
        )
    if body.observed_at.tzinfo is None:
        body.observed_at = body.observed_at.replace(tzinfo=timezone.utc)
    body.crop = body.crop.lower().strip()
    await svc.add_observation(body)
    return body


@router.get("/health/_seeded", include_in_schema=False)
async def seeded_at() -> dict[str, str]:
    return {"server_time": datetime.now(timezone.utc).isoformat()}
