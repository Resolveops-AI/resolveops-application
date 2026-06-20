from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "QuickHaul Transport API"
    env: str = "production"
    secret_key: str = "hello_welcome_to_quick_haul_transports"
    access_token_expire_minutes: int = 1440
    frontend_url: str = "http://localhost:5173"

    # Database & Cache
    mongo_uri: str = "mongodb://mongodb:27017"
    mongo_db_name: str = "quick_haul"
    redis_url: str = "redis://redis:6379/0"

    # SMTP Settings
    smtp_enabled: bool = True
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "sathviknbmath@gmail.com"
    smtp_password: str = "qgao dqvk jiut ktyhr"
    smtp_from_email: str = "sathviknbmath@gmail.com"
    smtp_from_name: str = "Quick Haul Support"
    smtp_use_tls: bool = False
    smtp_use_starttls: bool = True

    # Service URLs
    location_service_url: str = "http://location_service:8001"
    auth_service_url: str = "http://auth_service:8002"
    booking_service_url: str = "http://booking_service:8003"
    notification_service_url: str = "http://notification_service:8004"
    otp_service_url: str = "http://otp_service:8005"
    payment_service_url: str = "http://payment_service:8006"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
