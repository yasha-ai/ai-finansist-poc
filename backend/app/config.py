from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str = ""
    MINI_APP_URL: str = "https://poc.dyuzhev.dev"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/finansist"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@db:5432/finansist"

    # Payments (mock mode)
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    PAYMENT_MOCK: bool = True

    # App
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
