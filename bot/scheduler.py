"""Планировщик торговых задач по расписанию новостей."""

import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import settings
from bot.database import deactivate_event, list_events
from bot.models import NewsEvent
from bot.mt5_client import MT5Client

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Планировщик: за 5 минут до новости выставляет и двигает ордера."""

    def __init__(self, mt5: MT5Client) -> None:
        self.mt5 = mt5
        self.scheduler = AsyncIOScheduler()
        self._active_tasks: dict[int, asyncio.Task[None]] = {}

    def start(self) -> None:
        """Запустить планировщик."""
        self.scheduler.add_job(
            self._sync_events,
            "interval",
            seconds=30,
            id="sync_events",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("📅 Планировщик запущен")

    def stop(self) -> None:
        """Остановить планировщик и отменить все задачи."""
        for task in self._active_tasks.values():
            task.cancel()
        self._active_tasks.clear()
        self.scheduler.shutdown(wait=False)
        logger.info("📅 Планировщик остановлен")

    async def _sync_events(self) -> None:
        """Проверить расписание и запланировать торговлю."""
        events = list_events(only_active=True)
        now = datetime.now()

        for event in events:
            if event.id is None:
                continue

            # Пропускаем уже запущенные
            if event.id in self._active_tasks:
                continue

            start_time = event.event_date - timedelta(seconds=settings.pre_news_seconds)

            # Если время старта уже наступило или через <30 сек — запускаем
            if start_time <= now + timedelta(seconds=30):
                if event.event_date < now:
                    # Новость уже прошла — деактивируем
                    deactivate_event(event.id)
                    logger.info("⏭ Новость #%d пропущена (прошла)", event.id)
                    continue

                task = asyncio.create_task(self._trade_on_news(event))
                self._active_tasks[event.id] = task
                logger.info(
                    "🚀 Запущена торговля для %s (%s) — новость #%d",
                    event.symbol,
                    event.event_date.strftime("%H:%M:%S"),
                    event.id,
                )

    async def _trade_on_news(self, event: NewsEvent) -> None:
        """Основная торговая логика для одной новости."""
        assert event.id is not None
        symbol = event.symbol
        offset = settings.offset_points
        lot = settings.lot_size

        # Определяем множитель пункта (JPY пары: 0.01, остальные: 0.00001)
        if "JPY" in symbol.upper():
            point = 0.01
        else:
            point = 0.00001

        offset_price = offset * point
        buy_ticket: int | None = None
        sell_ticket: int | None = None

        try:
            # Ждём время начала (за 5 мин до новости)
            start_time = event.event_date - timedelta(seconds=settings.pre_news_seconds)
            now = datetime.now()
            if start_time > now:
                wait_sec = (start_time - now).total_seconds()
                logger.info(
                    "⏳ Ожидание %.0f сек до начала торговли по %s", wait_sec, symbol
                )
                await asyncio.sleep(wait_sec)

            # Получаем цену и выставляем ордера
            price = self.mt5.get_price(symbol)
            if price is None:
                logger.error("Не удалось получить цену %s — пропуск", symbol)
                return

            buy_price = round(price + offset_price, 5)
            sell_price = round(price - offset_price, 5)

            buy_ticket = self.mt5.place_buy_stop(symbol, buy_price, lot)
            sell_ticket = self.mt5.place_sell_stop(symbol, sell_price, lot)

            if buy_ticket is None or sell_ticket is None:
                logger.error("Не удалось выставить ордера для %s", symbol)
                return

            # Двигаем ордера каждые ~1.5 сек до момента новости
            while datetime.now() < event.event_date:
                await asyncio.sleep(settings.update_interval)

                if datetime.now() >= event.event_date:
                    break

                current_price = self.mt5.get_price(symbol)
                if current_price is None:
                    continue

                new_buy = round(current_price + offset_price, 5)
                new_sell = round(current_price - offset_price, 5)

                self.mt5.modify_order(buy_ticket, new_buy)
                self.mt5.modify_order(sell_ticket, new_sell)

            logger.info(
                "📰 Новость вышла! Ордера %s зафиксированы (buy=%s, sell=%s)",
                symbol,
                buy_ticket,
                sell_ticket,
            )

        except asyncio.CancelledError:
            logger.info("Торговля по %s отменена", symbol)
            # Отменяем ордера при отмене задачи
            if buy_ticket:
                self.mt5.cancel_order(buy_ticket)
            if sell_ticket:
                self.mt5.cancel_order(sell_ticket)
        finally:
            deactivate_event(event.id)
            self._active_tasks.pop(event.id, None)

    def get_active_count(self) -> int:
        """Количество активных торговых задач."""
        return len(self._active_tasks)
