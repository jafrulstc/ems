from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "Education Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    STORAGE_PROVIDER: Literal["minio", "aws", "s3"] = "minio"
    STORAGE_ENDPOINT: str | None = None
    STORAGE_ACCESS_KEY: str | None = None
    STORAGE_SECRET_KEY: str | None = None
    STORAGE_BUCKET_NAME: str | None = None
    STORAGE_SECURE: bool = False
    STORAGE_REGION: str | None = "auto"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
