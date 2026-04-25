from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    claude_model: str = "claude-opus-4-7"

    use_managed_agent: bool = False
    managed_agent_id: str = ""
    managed_environment_id: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
