"""Обработчики команд Telegram бота."""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings
from bot.database import add_event, delete_event, list_events
from bot.mt5_client import MT5Client
from bot.scheduler import TradingScheduler

logger = logging.getLogger(__name__)

# Глобальные ссылки (устанавливаются в main.py)
mt5_client: MT5Client | None = None
trading_scheduler: TradingScheduler | None = None


def set_dependencies(mt5: MT5Client, scheduler: TradingScheduler) -> None:
    """Установить зависимости для обработчиков."""
    global mt5_client, trading_scheduler
    mt5_client = mt5
    trading_scheduler = scheduler


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start — приветствие."""
    assert update.message is not None
    mode = "🔧 Demo" if settings.demo_mode else "🔴 Live MT5"
    text = (
        "📊 <b>Forex News Trading Bot</b>\n\n"
        f"Режим: {mode}\n\n"
        "Команды:\n"
        "/add_event &lt;дата&gt; &lt;время&gt; &lt;пара&gt; — добавить новость\n"
        "/list — расписание новостей\n"
        "/delete &lt;id&gt; — удалить новость\n"
        "/settings — текущие настройки\n"
        "/status — статус бота\n\n"
        "Формат даты: <code>2025-01-31 15:30 EURUSD</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_add_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /add_event — добавить новость в расписание."""
    assert update.message is not None

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Формат: /add_event <дата> <время> <пара>\n"
            "Пример: <code>/add_event 2025-01-31 15:30 EURUSD</code>",
            parse_mode="HTML",
        )
        return

    date_str = context.args[0]
    time_str = context.args[1]
    symbol = context.args[2].upper()

    try:
        event_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты/времени.\n"
            "Используйте: <code>YYYY-MM-DD HH:MM</code>",
            parse_mode="HTML",
        )
        return

    if event_date < datetime.now():
        await update.message.reply_text("❌ Дата уже прошла.")
        return

    description = " ".join(context.args[3:]) if len(context.args) > 3 else ""
    event_id = add_event(event_date, symbol, description)

    await update.message.reply_text(
        f"✅ Новость добавлена (#{event_id}):\n"
        f"📅 {event_date.strftime('%Y-%m-%d %H:%M')}\n"
        f"💱 {symbol}\n"
        f"{'📝 ' + description if description else ''}",
    )
    logger.info("Добавлена новость #%d: %s %s", event_id, event_date, symbol)


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /list — показать расписание."""
    assert update.message is not None

    events = list_events(only_active=True)
    if not events:
        await update.message.reply_text("📭 Расписание пусто.")
        return

    lines: list[str] = ["📋 <b>Расписание новостей:</b>\n"]
    for e in events:
        assert e.event_date is not None
        dt = e.event_date.strftime("%Y-%m-%d %H:%M")
        desc = f" — {e.description}" if e.description else ""
        lines.append(f"#{e.id} | {dt} | {e.symbol}{desc}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /delete — удалить новость."""
    assert update.message is not None

    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Формат: /delete <id>")
        return

    try:
        event_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом.")
        return

    if delete_event(event_id):
        await update.message.reply_text(f"🗑 Новость #{event_id} удалена.")
    else:
        await update.message.reply_text(f"❌ Новость #{event_id} не найдена.")


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /settings — показать настройки."""
    assert update.message is not None

    mode = "🔧 Demo (mock)" if settings.demo_mode else "🔴 Live MT5"
    text = (
        "⚙️ <b>Настройки:</b>\n\n"
        f"Режим: {mode}\n"
        f"Отступ ордеров: {settings.offset_points} пунктов\n"
        f"Размер лота: {settings.lot_size}\n"
        f"Старт до новости: {settings.pre_news_seconds} сек\n"
        f"Интервал обновления: {settings.update_interval} сек"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /status — статус бота."""
    assert update.message is not None
    assert mt5_client is not None
    assert trading_scheduler is not None

    events = list_events(only_active=True)
    active_trades = trading_scheduler.get_active_count()

    mt5_status = "✅ Подключён" if mt5_client.is_connected else "❌ Отключён"
    mode = "Demo" if mt5_client.is_demo else "Live"

    text = (
        "📊 <b>Статус бота:</b>\n\n"
        f"MT5: {mt5_status} ({mode})\n"
        f"Новостей в очереди: {len(events)}\n"
        f"Активных торговых задач: {active_trades}"
    )
    await update.message.reply_text(text, parse_mode="HTML")
