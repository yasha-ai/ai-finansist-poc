"""Клиент MetaTrader 5 с demo-заглушкой."""

import logging
import random
from dataclasses import dataclass, field

from bot.config import settings

logger = logging.getLogger(__name__)

# Попытка импорта MT5 (работает только на Windows)
try:
    import MetaTrader5 as mt5  # type: ignore[import-untyped]

    MT5_AVAILABLE = True
except ImportError:
    mt5 = None  # type: ignore[assignment]
    MT5_AVAILABLE = False


@dataclass
class MockOrder:
    """Мок отложенного ордера для demo-режима."""

    ticket: int
    symbol: str
    order_type: str
    price: float
    lot: float


class MT5Client:
    """Обёртка над MetaTrader5 с fallback на demo-режим."""

    def __init__(self) -> None:
        self._connected: bool = False
        self._demo: bool = settings.demo_mode or not MT5_AVAILABLE
        self._mock_orders: dict[int, MockOrder] = {}
        self._mock_ticket_counter: int = 1000
        self._mock_prices: dict[str, float] = field(default_factory=dict) if False else {}

    def connect(self) -> bool:
        """Подключиться к MT5 или активировать demo-режим."""
        if self._demo:
            logger.info("🔧 Demo-режим: MT5 эмулируется")
            self._connected = True
            return True

        if not mt5.initialize(path=settings.mt5_path or None):
            logger.error("Не удалось инициализировать MT5: %s", mt5.last_error())
            return False

        if settings.mt5_login:
            auth = mt5.login(
                login=settings.mt5_login,
                password=settings.mt5_password,
                server=settings.mt5_server,
            )
            if not auth:
                logger.error("Ошибка авторизации MT5: %s", mt5.last_error())
                return False

        self._connected = True
        logger.info("✅ Подключено к MT5")
        return True

    def disconnect(self) -> None:
        """Отключиться от MT5."""
        if not self._demo and MT5_AVAILABLE:
            mt5.shutdown()
        self._connected = False
        logger.info("MT5 отключён")

    def get_price(self, symbol: str) -> float | None:
        """Получить текущую цену (bid) по символу."""
        if self._demo:
            # Генерируем стабильную mock-цену с небольшим шумом
            if symbol not in self._mock_prices:
                base_prices: dict[str, float] = {
                    "EURUSD": 1.08500,
                    "GBPUSD": 1.26300,
                    "USDJPY": 149.500,
                    "USDCHF": 0.87800,
                    "AUDUSD": 0.65200,
                    "USDCAD": 1.35600,
                    "NZDUSD": 0.60100,
                }
                self._mock_prices[symbol] = base_prices.get(symbol, 1.10000)
            # Добавляем рыночный шум ±50 пунктов (5-й знак)
            noise = random.uniform(-0.00050, 0.00050)
            return round(self._mock_prices[symbol] + noise, 5)

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error("Не удалось получить цену %s", symbol)
            return None
        return float(tick.bid)

    def place_buy_stop(self, symbol: str, price: float, lot: float) -> int | None:
        """Выставить Buy Stop ордер. Возвращает ticket."""
        if self._demo:
            self._mock_ticket_counter += 1
            ticket = self._mock_ticket_counter
            self._mock_orders[ticket] = MockOrder(
                ticket=ticket,
                symbol=symbol,
                order_type="BUY_STOP",
                price=price,
                lot=lot,
            )
            logger.info(
                "📈 [DEMO] Buy Stop: %s @ %.5f (ticket=%d)", symbol, price, ticket
            )
            return ticket

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": price,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Ошибка Buy Stop: %s", result)
            return None
        logger.info("📈 Buy Stop: %s @ %.5f (ticket=%d)", symbol, price, result.order)
        return int(result.order)

    def place_sell_stop(self, symbol: str, price: float, lot: float) -> int | None:
        """Выставить Sell Stop ордер. Возвращает ticket."""
        if self._demo:
            self._mock_ticket_counter += 1
            ticket = self._mock_ticket_counter
            self._mock_orders[ticket] = MockOrder(
                ticket=ticket,
                symbol=symbol,
                order_type="SELL_STOP",
                price=price,
                lot=lot,
            )
            logger.info(
                "📉 [DEMO] Sell Stop: %s @ %.5f (ticket=%d)", symbol, price, ticket
            )
            return ticket

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": price,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Ошибка Sell Stop: %s", result)
            return None
        logger.info("📉 Sell Stop: %s @ %.5f (ticket=%d)", symbol, price, result.order)
        return int(result.order)

    def modify_order(self, ticket: int, new_price: float) -> bool:
        """Переместить отложенный ордер на новую цену."""
        if self._demo:
            if ticket in self._mock_orders:
                old_price = self._mock_orders[ticket].price
                self._mock_orders[ticket].price = new_price
                logger.debug(
                    "🔄 [DEMO] Ордер %d: %.5f → %.5f", ticket, old_price, new_price
                )
                return True
            return False

        order_info = mt5.orders_get(ticket=ticket)
        if not order_info:
            logger.error("Ордер %d не найден", ticket)
            return False

        request = {
            "action": mt5.TRADE_ACTION_MODIFY,
            "order": ticket,
            "price": new_price,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Ошибка модификации ордера %d: %s", ticket, result)
            return False
        return True

    def cancel_order(self, ticket: int) -> bool:
        """Отменить отложенный ордер."""
        if self._demo:
            if ticket in self._mock_orders:
                del self._mock_orders[ticket]
                logger.info("❌ [DEMO] Ордер %d отменён", ticket)
                return True
            return False

        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": ticket,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Ошибка отмены ордера %d: %s", ticket, result)
            return False
        logger.info("❌ Ордер %d отменён", ticket)
        return True

    @property
    def is_demo(self) -> bool:
        """Работаем в demo-режиме?"""
        return self._demo

    @property
    def is_connected(self) -> bool:
        """Подключены к MT5?"""
        return self._connected
