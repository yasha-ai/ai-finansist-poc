"""Telegram Bot for AI Finansist."""
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🎓 Открыть кабинет",
            web_app=WebAppInfo(url=settings.MINI_APP_URL),
        )],
        [
            InlineKeyboardButton("📜 Каталог", callback_data="catalog"),
            InlineKeyboardButton("🎲 Розыгрыши", callback_data="raffles"),
        ],
        [InlineKeyboardButton("🤝 Благотворительность", callback_data="charity")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n\n"
        "Я *AI‑Финансист* — помощник в мире финансовой грамотности.\n\n"
        "📜 Покупай сертификаты на консультации с AI\n"
        "🎁 Участвуй в бесплатных розыгрышах\n"
        "🤝 Голосуй за благотворительные проекты\n"
        "💡 Получай персональные финансовые советы\n\n"
        "Нажми кнопку ниже, чтобы открыть личный кабинет:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "📜 *Доступные сертификаты:*\n\n"
        "1️⃣ *Базовая финансовая грамотность* — 1 000₽\n"
        "   Бюджет, накопления, долги\n\n"
        "2️⃣ *Инвестиции для начинающих* — 2 500₽\n"
        "   Пассивный доход, портфель\n\n"
        "3️⃣ *Налоговая оптимизация* — 5 000₽\n"
        "   Вычеты, оптимизация для ИП\n\n"
        "Открой Mini App для покупки! 👇"
    )

    keyboard = [[InlineKeyboardButton(
        "🛒 Купить сертификат",
        web_app=WebAppInfo(url=settings.MINI_APP_URL),
    )]]

    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def raffles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton(
        "🎲 Участвовать",
        web_app=WebAppInfo(url=f"{settings.MINI_APP_URL}?tab=raffles"),
    )]]

    await query.edit_message_text(
        "🎲 *Розыгрыши сертификатов*\n\n"
        "Участвуй бесплатно — выигрывай AI-консультации!\n\n"
        "🎁 Сейчас разыгрывается:\n"
        "*Инвестиции для начинающих* (2 500₽)\n"
        "⏰ Осталось 7 дней\n\n"
        "Открой Mini App для участия 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def charity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton(
        "🤝 Голосовать",
        web_app=WebAppInfo(url=f"{settings.MINI_APP_URL}?tab=charity"),
    )]]

    await query.edit_message_text(
        "🤝 *Голосование за благотворительность*\n\n"
        "Выбери проект, которому мы направим часть средств:\n\n"
        "1. 📚 Финграмотность для детей — 40%\n"
        "2. 👴 Помощь пенсионерам — 27%\n"
        "3. 🚀 Поддержка предпринимателей — 33%\n\n"
        "Голосуй в Mini App 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def main():
    app = Application.builder().token(settings.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(catalog_callback, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(raffles_callback, pattern="^raffles$"))
    app.add_handler(CallbackQueryHandler(charity_callback, pattern="^charity$"))

    logger.info("🤖 Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
