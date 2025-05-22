from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
import enum

from src.database import Base

class Role(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    role: Mapped[Role]
    api_key_hash: Mapped[str] = mapped_column(unique=True)
    encrypted_api_key: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
