# Forex News Trading Bot (POC)

Telegram-бот для автоматической торговли на экономических новостях Forex.

## Логика работы

1. Пользователь добавляет расписание экономических новостей (дата, время, валютная пара)
2. За 5 минут до новости бот выставляет 2 отложенных ордера:
   - **Buy Stop**: текущая цена + 200 пунктов
   - **Sell Stop**: текущая цена - 200 пунктов
3. Каждые 1-2 секунды бот переставляет ордера относительно текущей цены
4. В момент выхода новости бот прекращает двигать ордера — они фиксируются

## Стек

- Python 3.12
- python-telegram-bot (async)
- MetaTrader5 (Windows) / Demo-режим (mock)
- APScheduler
- SQLite
- Pydantic

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и список команд |
| `/add_event <дата> <время> <пара>` | Добавить новость |
| `/list` | Показать расписание |
| `/delete <id>` | Удалить новость |
| `/settings` | Текущие настройки |
| `/status` | Статус бота и MT5 |

Пример: `/add_event 2025-01-31 15:30 EURUSD`

## Запуск

```bash
cp .env.example .env
# Заполните TELEGRAM_TOKEN в .env

pip install -r requirements.txt
python -m bot.main
```

## Docker

```bash
docker build -t forex-bot .
docker run --env-file .env forex-bot
```

## Demo-режим

По умолчанию бот работает в demo-режиме (`DEMO_MODE=True`) — MT5 эмулируется mock-ценами. Для реальной торговли установите `DEMO_MODE=False` и заполните MT5-параметры в `.env`.

> **Важно:** MetaTrader5 работает только на Windows. На Linux/macOS используйте demo-режим.
