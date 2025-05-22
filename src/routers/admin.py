from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from src.users.service import is_user_admin, delete_user
from src.users.schemas import UserModel
from src.instruments.service import create_instrument, delete_instrument, get_instrument_id
from src.instruments.schemas import CreateInstrument
from src.balances.service import deposit, withdraw
from src.balances.schemas import Balance


class Result(BaseModel):
    success: bool


admin_router = APIRouter(prefix="/admin", tags=["admin"])


async def get_authorization(authorization: str | None = Header(default=None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    return authorization


@admin_router.post("/instrument", response_model=Result)
async def add_instrument(instrument: CreateInstrument, authorization: str = Depends(get_authorization)):
    await check_admin(authorization)
    await create_instrument(instrument)

    return Result(success=True)

@admin_router.delete("/user/{user_id}", response_model=UserModel, tags=["user"])
async def user_delete(user_id: str, authorization: str | None = Depends(get_authorization)):
    await check_admin(authorization)
    return await delete_user(user_id)

@admin_router.delete("/instrument/{ticker}", response_model=Result)
async def instrument_delete(ticker: str, authorization: str | None = Depends(get_authorization)):
    await check_admin(authorization)
    await delete_instrument(ticker)
    return Result(success=True)

@admin_router.post("/balance/deposit", response_model=Result, tags=["balance"])
async def balance_deposit(balance: Balance, authorization: str | None = Depends(get_authorization)):
    await check_admin(authorization)
    instrument_id = await get_instrument_id(balance.ticker)
    if not instrument_id:
        raise HTTPException(status_code=400, detail="Instrument not exists")
    await deposit(
        user_id=balance.user_id, 
        instrument_id=instrument_id,
        amount=balance.amount
    )
    return Result(success=True)

@admin_router.post("/balance/withdraw", response_model=Result, tags=["balance"])
async def balance_withdraw(balance: Balance, authorization: str | None = Depends(get_authorization)):
    await check_admin(authorization)
    instrument_id = await get_instrument_id(balance.ticker)
    if not instrument_id:
        raise HTTPException(status_code=400, detail="Instrument not exists")
    await withdraw(
        user_id=balance.user_id, 
        instrument_id=instrument_id,
        amount=balance.amount
    )
    return Result(success=True)

async def check_admin(authorization: str | None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    
    if not authorization.startswith("TOKEN "):
        raise HTTPException(status_code=401, detail=f"Incorrect api-key: {authorization}")
    
    token = authorization.replace("TOKEN ", "")
    admin = await is_user_admin(token)
    if not admin:
        raise HTTPException(status_code=403, detail=f"User is not admin")
