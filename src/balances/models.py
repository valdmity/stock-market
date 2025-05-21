from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from src.database import Base

class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    instrument_id: Mapped[UUID] = mapped_column(ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    amount: Mapped[int] = mapped_column(default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'instrument_id', name='uix_user_instrument'),
    )

