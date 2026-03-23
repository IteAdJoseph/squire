from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_name: str = "reminda"
    log_level: str = "INFO"
    tz: str = "America/Sao_Paulo"
    frontend_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    # Database & cache
    database_url: str = "postgresql://localhost/reminda"
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    encryption_key: str = "dev-encryption-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 h

    # WhatsApp (Meta Cloud API)
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""

    # Pix (reservado para PSP futuro)
    pix_provider_api_key: str = ""
    pix_provider_webhook_secret: str = ""


settings = Settings()
