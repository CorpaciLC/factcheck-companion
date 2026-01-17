from pydantic_settings import BaseSettings
from functools import lru_cache




class Settings(BaseSettings):
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = "whatsapp:+14155238886"


    # Google Fact Check API
    GOOGLE_API_KEY: str = ""

    # Serper for search fallback (optional)
    SERPER_API_KEY: str = ""


    # Supabase for query logging
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""


    # App settings
    DEBUG: bool = False
    DASHBOARD_URL: str = ""  # Public dashboard URL to show in welcome message


    class Config:
        env_file = ".env"




@lru_cache()
def get_settings() -> Settings:
    return Settings()




settings = get_settings()





