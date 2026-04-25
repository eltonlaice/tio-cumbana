"""Weather MCP server for Tio Cumbana.

Exposes a single tool, ``get_weather``, that the vigilance agent calls
once per tick to decide whether weather conditions warrant interrupting
the farmer.

Why an MCP server (and not a direct httpx call inside the backend)?
-------------------------------------------------------------------
Two reasons:

1. **Decoupling the brain from the hands.** The Managed Agent (Tio
   Cumbana's autonomous loop) stays focused on agronomic decisions.
   Weather lookups are a tool it consumes, not part of its prompt.
   Tomorrow we add ``get_market_prices``, ``read_phenology``, and
   ``check_supplier_stock`` here without touching the agent.
2. **Reusability.** The same MCP server can power Claude Code locally,
   Claude Desktop, and the production Managed Agent — one tool, three
   surfaces. That is the MCP value proposition.

Data source: Open-Meteo (https://open-meteo.com/) — free, no API key,
covers Mozambique. Hourly forecast suffices for the mildew/wind/heat
windows that matter for cucumber and pepper in Maluana.
"""

from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tio-cumbana-weather")

OPEN_METEO = "https://api.open-meteo.com/v1/forecast"


@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Return next-24h weather for a given coordinate.

    Args:
        latitude: decimal degrees, e.g. -25.45 for Maluana, Marracuene.
        longitude: decimal degrees, e.g. 32.62 for Maluana, Marracuene.

    Returns a dict with:
        - current: temperature_2m, relative_humidity_2m, wind_speed_10m
        - hourly: lists of temperature_2m, relative_humidity_2m,
          precipitation, wind_speed_10m for the next 24 hours
        - mildew_risk: heuristic boolean — true when humidity > 85%
          for 3+ overnight hours and temperature stays in 15-22 °C window.
          That window is the canonical *Pseudoperonospora cubensis*
          (cucumber downy mildew) infection envelope.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "forecast_days": 1,
        "timezone": "Africa/Maputo",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(OPEN_METEO, params=params)
        resp.raise_for_status()
        data = resp.json()

    return {
        "current": data.get("current"),
        "hourly": data.get("hourly"),
        "mildew_risk": _mildew_risk(data.get("hourly", {})),
    }


def _mildew_risk(hourly: dict[str, list[Any]]) -> bool:
    rh = hourly.get("relative_humidity_2m") or []
    temp = hourly.get("temperature_2m") or []
    overnight_humid = sum(
        1 for h, t in zip(rh, temp) if h is not None and t is not None and h > 85 and 15 <= t <= 22
    )
    return overnight_humid >= 3


if __name__ == "__main__":
    mcp.run()
