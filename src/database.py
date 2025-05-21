from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False
)

session_factory = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass