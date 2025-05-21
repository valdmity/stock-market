from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from src.database import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    ticker: Mapped[str] = mapped_column(unique=True)
