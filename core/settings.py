from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent / "uploads")
    DB_PATH: str = "mapping.db"
    ALLOWED_EXT: str = ".csv,.xlsx,.json"

    # S3
    S3_ENDPOINT: str | None = None
    S3_REGION: str = "ru-central1"
    S3_BUCKET: str | None = None
    S3_KEY: str | None = None
    S3_SECRET: str | None = None

    #API
    SENDER_ENDPOINT: str = "https://api.partner.com/v1/upload"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
