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
