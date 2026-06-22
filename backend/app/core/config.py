from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    DATABASE_URL: str = ""
    
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    
    REDIS_URL: Optional[str] = None
    
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: Optional[str] = None
    SARVAM_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None
    
    FRONTEND_URL: Optional[str] = None
    
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://voicera-backend-production.up.railway.app/api/v1/calendar/callback"
    BREVO_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
