from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VerifPlatform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "changeme_super_secret_key_at_least_32_chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    API_SECRET: str = "bot_api_secret_shared_with_bot"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://verifuser:verifpass@localhost:5432/verifdb"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram
    BOT_TOKEN: str = ""
    ADMIN_IDS: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Defaults
    DEFAULT_MIN_DEPOSIT: float = 5.0
    DEFAULT_MIN_WITHDRAWAL: float = 5.0
    DEFAULT_REFERRAL_REWARD: float = 2.0

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
