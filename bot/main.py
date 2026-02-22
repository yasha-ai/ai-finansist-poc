"""Точка входа: запуск Telegram бота и планировщика."""

import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from bot.config import settings
from bot.handlers import (
    cmd_add_event,
    cmd_delete,
    cmd_list,
    cmd_settings,
    cmd_start,
    cmd_status,
    set_dependencies,
)
from bot.mt5_client import MT5Client
from bot.scheduler import TradingScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Инициализация и запуск бота."""
    if not settings.telegram_token:
        logger.error("❌ TELEGRAM_TOKEN не задан! Укажите его в .env")
        return

    # MT5
    mt5 = MT5Client()
    mt5.connect()

    # Планировщик
    scheduler = TradingScheduler(mt5)
    scheduler.start()

    # Передаём зависимости в обработчики
    set_dependencies(mt5, scheduler)

    # Telegram бот
    app = ApplicationBuilder().token(settings.telegram_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("add_event", cmd_add_event))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("delete", cmd_delete))
    app.add_handler(CommandHandler("settings", cmd_settings))
    app.add_handler(CommandHandler("status", cmd_status))

    logger.info("🤖 Бот запущен! Режим: %s", "Demo" if mt5.is_demo else "Live MT5")
    app.run_polling(drop_pending_updates=True)

    # Cleanup
    scheduler.stop()
    mt5.disconnect()


if __name__ == "__main__":
    main()
