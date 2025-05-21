from fastapi import APIRouter

from src.users.service import UserModel, UserCreate, create_user
from src.instruments.service import InstrumentModel, get_instruments
from src.orders.service import OrderBook, get_orderbook
from src.transactions.service import TransactionHistrory, get_history

public_router = APIRouter(prefix="/public", tags=["public"])

@public_router.post("/register", response_model=UserModel)
async def register(user: UserCreate):
    return await create_user(user)

@public_router.get("/instrument", response_model=list[InstrumentModel])
async def get_all_instruments():
    return await get_instruments()

@public_router.get("/orderbook/{ticker}", response_model=OrderBook)
async def get_order_book(ticker: str, limit: int = 10):
    return await get_orderbook(ticker, limit)

@public_router.get("/transactions/{ticker}", response_model=list[TransactionHistrory])
async def get_transactions(ticker: str, limit: int = 10):
    return await get_history(ticker, limit)