"""Pydantic-модели данных."""

from datetime import datetime

from pydantic import BaseModel


class NewsEvent(BaseModel):
    """Экономическая новость."""

    id: int | None = None
    event_date: datetime
    symbol: str  # например EURUSD
    description: str = ""
    active: bool = True


class PendingOrder(BaseModel):
    """Отложенный ордер."""

    ticket: int
    symbol: str
    order_type: str  # BUY_STOP / SELL_STOP
    price: float
    lot: float
