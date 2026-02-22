"""Конфигурация бота."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    # Telegram (принимает TELEGRAM_TOKEN или BOT_TOKEN)
    telegram_token: str = ""
    bot_token: str = ""

    # MetaTrader 5
    mt5_login: int = 0
    mt5_password: str = ""
    mt5_server: str = ""
    mt5_path: str = ""

    # Торговля
    offset_points: int = 200
    lot_size: float = 0.01
    pre_news_seconds: int = 300  # 5 минут до новости
    update_interval: float = 1.5  # секунд между обновлениями ордеров

    # Режим demo (mock MT5)
    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


_s = Settings()
# Fallback: если telegram_token пуст, используем bot_token
if not _s.telegram_token and _s.bot_token:
    _s.telegram_token = _s.bot_token
settings = _s
