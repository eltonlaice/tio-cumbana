"""Market-prices MCP server for Tio Cumbana.

Exposes Zimpeto wholesale + retail prices to the vigilance agent and to
any human operator using Claude Desktop / Claude Code. The data comes
from the community price pool (`backend/app/services/market_prices.py`),
which is updated by the farmers themselves: when Dona Maria walks to
Zimpeto she contributes the prices she saw, and the agent serves the
aggregated view back to the next farmer who's about to make the trip.

This MCP server does NOT keep its own database — it is a read/write
proxy over the backend's REST endpoints. One source of truth.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tio-cumbana-market-prices")

API_URL = os.environ.get("TIO_CUMBANA_API_URL", "http://localhost:8000")


@mcp.tool()
async def get_zimpeto_prices(crop: str) -> dict[str, Any]:
    """Latest wholesale + retail prices at Mercado do Zimpeto for a given crop.

    Returns the latest contributed price, the 7-day median, the number of
    contributors in the last 7 days, and when the most recent observation
    came in. Prices are MZN per kilogram.

    Args:
        crop: lowercase, accent-stripped crop name — pepino, tomate,
              cebola, alho, pimento, couve, etc.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{API_URL}/api/market-prices/{crop.lower().strip()}")
        if resp.status_code == 404:
            return {"crop": crop, "available": False, "reason": "no observations in the last 7 days"}
        resp.raise_for_status()
        return {**resp.json(), "available": True}


@mcp.tool()
async def list_zimpeto_market() -> list[dict[str, Any]]:
    """All crops with at least one observation in the last 7 days at Zimpeto."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{API_URL}/api/market-prices")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def contribute_price(
    contributor_phone: str,
    crop: str,
    price_wholesale: float | None = None,
    price_retail: float | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Append a new price observation to the community pool.

    Use when a farmer (or a human operator with their permission) reports
    a fresh price seen at Zimpeto. At least one of wholesale / retail
    must be provided.
    """
    payload = {
        "contributor_phone": contributor_phone,
        "crop": crop.lower().strip(),
        "price_wholesale": price_wholesale,
        "price_retail": price_retail,
        "market": "Zimpeto",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "note": note,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(f"{API_URL}/api/market-prices", json=payload)
        resp.raise_for_status()
        return dict(resp.json())


if __name__ == "__main__":
    mcp.run()
