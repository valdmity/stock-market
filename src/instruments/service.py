from fastapi import HTTPException
from sqlalchemy import insert, select, delete
from uuid import uuid4

from src.database import session_factory
from src.instruments.models import Instrument
from src.instruments.schemas import CreateInstrument, InstrumentModel


async def create_instrument(instrument: CreateInstrument) -> InstrumentModel:
    instruments = Instrument.__table__
    query = insert(instruments).values(
        id=uuid4(),
        name=instrument.name,
        ticker=instrument.ticker
    ).returning(instruments.c.id, instruments.c.name, instruments.c.ticker)
    
    try:
        async with session_factory() as session:
            result = await session.execute(query)
            entity = result.fetchone()
            await session.commit()
            return InstrumentModel(
                name=entity.name,
                ticker=entity.ticker
            )
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Instrument with this name or ticker already exists")
        raise e

async def get_instruments() -> list[Instrument]:
    async with session_factory() as session:
        result = await session.execute(select(Instrument.name, Instrument.ticker))
        return [InstrumentModel(name=i.name, ticker=i.ticker) for i in result.all()]

async def get_instrument_id(ticker: str) -> str | None:
    async with session_factory() as session:
        result = await session.execute(select(Instrument.id).where(Instrument.ticker == ticker))
        row = result.first()
        return str(row.id) if row else None
    
async def delete_instrument(ticker: str):
    stmt = delete(Instrument).where(Instrument.ticker == ticker)
    async with session_factory() as session:
        await session.execute(stmt)
        await session.commit()
