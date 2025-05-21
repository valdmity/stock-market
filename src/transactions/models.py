from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime
from pytz import UTC

from src.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    instrument_id: Mapped[UUID] = mapped_column(ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    amount: Mapped[int] = mapped_column(default=0, nullable=False)
    timestamp: Mapped[str] = mapped_column(default=str(datetime.now(UTC)))
    price: Mapped[int | None] = mapped_column(default=None, nullable=True)
