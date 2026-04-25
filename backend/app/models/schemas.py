from datetime import datetime

from pydantic import BaseModel, Field


class FarmerProfile(BaseModel):
    phone: str
    name: str
    location: str
    crops: list[str]
    planting_dates: dict[str, str] = Field(default_factory=dict)  # crop → ISO date
    soil: str = ""
    preferences: list[str] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)  # short past-interaction notes
    language_mix: str = "pt-dominant"  # pt-dominant | mixed | changana-dominant


class ConsultResponse(BaseModel):
    text: str
    audio_b64: str | None = None
    audio_mime: str = "audio/mpeg"
    farmer: FarmerProfile


class ProactiveRequest(BaseModel):
    farmer_phone: str
    trigger: str = "mildew_morning"  # scripted trigger key


class ProactiveResponse(BaseModel):
    text: str
    audio_b64: str | None = None
    audio_mime: str = "audio/mpeg"
    farmer: FarmerProfile
    trigger: str


class MarketPriceUpdate(BaseModel):
    """A single price observation contributed by a farmer at a market."""

    contributor_phone: str
    crop: str  # canonical lowercase: pepino, tomate, cebola, alho, pimento, ...
    price_wholesale: float | None = Field(default=None, ge=0)  # MZN per kg, grossista
    price_retail: float | None = Field(default=None, ge=0)  # MZN per kg, retalho
    market: str = "Zimpeto"  # default the central wholesale market
    observed_at: datetime
    note: str | None = None  # e.g. "stock low", "imported"


class MarketPriceSnapshot(BaseModel):
    """Aggregated view per crop, computed over a rolling 24h window.

    Single observations are NEVER served as authoritative prices. We require
    at least two distinct contributors in the last 24h to mark a crop
    `confirmed`. Until confirmed, the median is still computed but the
    consumer (agent or UI) should treat it as provisional.
    """

    crop: str
    market: str
    confirmed: bool  # >= 2 distinct contributors in last 24h
    median_wholesale: float | None
    median_retail: float | None
    min_wholesale: float | None
    max_wholesale: float | None
    min_retail: float | None
    max_retail: float | None
    contributors_24h: int
    sample_size_24h: int
    last_observed_at: datetime | None
