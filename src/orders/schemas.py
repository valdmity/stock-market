from pydantic import BaseModel, Field

from src.orders.models import Direction, Status


class LimitOrderBody(BaseModel):
    direction: Direction
    qty: int = Field(ge=1)
    price: int = Field(gt=0)
    ticker: str

class MarketOrderBody(BaseModel):
    direction: Direction
    qty: int = Field(ge=1)
    ticker: str

class LimitOrder(BaseModel):
    id: str
    status: Status
    user_id: str
    timestamp: str
    body: LimitOrderBody
    filled: int

class MarketOrder(BaseModel):
    id: str
    status: Status
    user_id: str
    timestamp: str
    body: MarketOrderBody

class OrderBookItem(BaseModel):
    qty: int
    price: int

class OrderBook(BaseModel):
    bid_levels: list[OrderBookItem]
    ask_levels: list[OrderBookItem]
