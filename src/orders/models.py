from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from enum import Enum
from datetime import datetime
from pytz import UTC

from src.database import Base


class Status(Enum):
    NEW = "NEW"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"

class Direction(Enum):
    BUY = "BUY"
    SELL = "SELL"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    instrument_id: Mapped[UUID] = mapped_column(ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[Status] = mapped_column(default=Status.NEW)
    direction: Mapped[Direction]
    timestamp: Mapped[str] = mapped_column(default=str(datetime.now(UTC)))
    price: Mapped[int | None] = mapped_column(default=None, nullable=True)
    qty: Mapped[int] = mapped_column(nullable=False)
    filled: Mapped[int | None] = mapped_column(default=None, nullable=True)
