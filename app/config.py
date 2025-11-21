from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Must match .env keys (case-insensitive)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DATABASE_URL: str
    X_SECRET: str

    DRONES_API: str
    DRONES_LIST_API: str

    REDIS_URL: str

    LOG_TO_FILE: int = 0

    class Config:
        env_file = ".env"
        extra = "ignore"   # Ignore any unused vars to prevent crashes


settings = Settings()
