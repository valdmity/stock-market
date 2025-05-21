from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from uuid import uuid4
from sqlalchemy import update, text, select

from src.database import session_factory
from src.balances.models import Balance


async def deposit(user_id: str, instrument_id: str, amount: int):
    stmt = insert(Balance).values(
        id=uuid4(),
        user_id=user_id,
        instrument_id=instrument_id,
        amount=amount
    ).on_conflict_do_update(
        index_elements=['user_id', 'instrument_id'],
        set_={'amount': Balance.amount + amount}
    )
    
    async with session_factory() as session:
        await session.execute(stmt)
        await session.commit()

async def withdraw(user_id: str, instrument_id: str, amount: int):
    async with session_factory() as session:
        result = await session.execute(
            text("SELECT amount FROM balances WHERE user_id = :user_id AND ticker = :instrument_id FOR UPDATE"),
            {"user_id": user_id, "instrument_id": instrument_id}
        )
        current = result.first()

        if not current or current.amount < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        await session.execute(
            update(Balance)
                .where(Balance.user_id == user_id, Balance.instrument_id == instrument_id)
                .values(amount=Balance.amount - amount)
        )
        await session.commit()

async def get_all(user_id: str) -> dict[str, int]:
    query = select(Balance.ticker, Balance.amount).where(Balance.user_id == user_id, Balance.amount > 0)
    async with session_factory() as session:
        result = await session.execute(query)
        balances = {row.ticker: row.amount for row in result.fetchall()}
        return balances
