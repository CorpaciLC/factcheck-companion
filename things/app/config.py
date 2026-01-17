from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache




class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = "whatsapp:+14155238886"


    # Google Fact Check API
    GOOGLE_API_KEY: str = ""

    # Serper for search fallback (optional)
    SERPER_API_KEY: str = ""


    # LLM (direct OpenAI)
    # - Set OPENAI_API_KEY to enable
    # - Optionally set OPENAI_MODEL (e.g. "gpt-4o-mini")
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"


    # LLM (preferred: OpenRouter)
    # - Set OPENROUTER_API_KEY to enable
    # - Optionally set OPENROUTER_MODEL (e.g. "openai/gpt-4o-mini")
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = ""  # optional "HTTP-Referer" header
    OPENROUTER_APP_NAME: str = ""  # optional "X-Title" header


    # LLM (optional: Azure OpenAI)
    # If LLM_PROVIDER is "azure", you must set these.
    LLM_PROVIDER: str = "auto"  # auto | openai | openrouter | azure
    LLM_MODEL: str = "gpt-4o-mini"  # Azure logical model name OR OpenAI-style name (see provider)
    LLM_API_KEY: str = ""  # Azure OpenAI key
    LLM_ENDPOINT: str = ""  # Azure endpoint, e.g. https://<resource>.openai.azure.com
    LLM_API_VERSION: str = "2024-02-15-preview"


    # Supabase for query logging
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""


    # App settings
    DEBUG: bool = False
    DASHBOARD_URL: str = ""  # Public dashboard URL to show in welcome message


@lru_cache()
def get_settings() -> Settings:
    return Settings()




settings = get_settings()


def reload_settings() -> Settings:
    """Reload settings from environment (useful for tests)."""
    get_settings.cache_clear()
    global settings
    settings = get_settings()
    return settings





