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
    """Aggregated view per crop returned to consumers (the agent or the frontend)."""

    crop: str
    market: str
    latest_wholesale: float | None
    latest_retail: float | None
    median_wholesale_7d: float | None
    median_retail_7d: float | None
    sample_size_7d: int
    last_observed_at: datetime | None
    contributors_7d: int
