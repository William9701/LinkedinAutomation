from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LinkedIn (email/password optional if using access_token)
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    linkedin_access_token: str

    # Gemini AI
    gemini_api_key: str

    # Image Generation (Optional)
    openai_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None

    # Scheduling
    morning_post_time: str = "09:00"
    evening_post_time: str = "18:00"
    timezone: str = "UTC"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
