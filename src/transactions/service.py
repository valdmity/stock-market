from sqlalchemy import desc, select

from src.database import session_factory
from src.transactions.models import Transaction
from src.instruments.models import Instrument
from src.transactions.schemas import TransactionHistrory


async def get_history(ticker: str, limit: int) -> list[TransactionHistrory]:
    query = select(
        Instrument.ticker,
        Transaction.price,
        Transaction.amount,
        Transaction.timestamp
    ).select_from(
        Transaction
    ).join(
        Instrument,
        Instrument.id == Transaction.instrument_id
    ).where(
        Instrument.ticker == ticker
    ).order_by(
        desc(Transaction.timestamp)
    ).limit(limit)
    async with session_factory() as session:
        result = await session.execute(query)
        return [
            TransactionHistrory(
                ticker=t.ticker,
                price=t.price,
                amount=t.amount,
                timestamp=t.timestamp
            ) for t in result.all()
        ]
