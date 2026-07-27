from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://zimrental:zimrental123@localhost:5432/zimrental"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # SMS
    SMS_API_KEY: str = ""
    SMS_SENDER_ID: str = "ZimRental"
    SMS_PROVIDER: str = "africas_talking"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
