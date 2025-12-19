from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Loops API"
    app_version: str = "0.1.0"
    debug: bool = False

    # API settings
    api_v1_prefix: str = "/api/v1"

    # CORS settings
    allowed_origins: list[str] = ["*"]

    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/loops"
    database_echo: bool = False

    # Supabase settings (New API Key System - 2025+)
    supabase_url: str = "https://your-project.supabase.co"
    supabase_publishable_key: str = "sb_publishable_xxx"
    # Secret key: for admin operations (user deletion, password reset, etc.)
    supabase_secret_key: str = ""

    # OpenAI / LLM settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # OpenAI / TTS settings
    openai_tts_model: str = "tts-1"
    openai_tts_default_voice: str = "alloy"

    # TTS caching / rate limit
    tts_cache_ttl_seconds: int = 86400
    tts_cache_max_entries: int = 1024
    tts_rate_limit_requests: int = 30
    tts_rate_limit_window_seconds: int = 300
    # Gemini image generation (Google GenAI SDK)
    gemini_api_key: str = ""  # GEMINI_API_KEY
    gemini_image_model: str = "gemini-3-pro-image-preview"

    # Supabase Storage
    supabase_storage_bucket: str = "card-images"

    model_config = SettingsConfigDict(
        # Load repo-root .env regardless of current working directory.
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )


settings = Settings()
