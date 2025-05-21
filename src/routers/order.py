from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from src.orders.service import create_order, get_orders, get_order, cancel_order
from src.orders.schemas import MarketOrderBody, LimitOrderBody, LimitOrder, MarketOrder
from src.users.service import get_user_id

order_router = APIRouter(prefix="/order", tags=["order"])

header_scheme = APIKeyHeader(name="authorization", auto_error=False)

class CreateOrderResult(BaseModel):
    success: bool
    order_id: str

class CancelOrderResult(BaseModel):
    success: bool

@order_router.post("", response_model=CreateOrderResult)
async def create(order: MarketOrderBody | LimitOrderBody, authorization: str | None = Depends(header_scheme)):
    user_id = await parse_user_id(authorization)
    order_id = await create_order(user_id, order)
    return CreateOrderResult(success=True, order_id=order_id)

@order_router.get("", response_model=list[MarketOrder | LimitOrder])
async def get_all(authorization: str | None = Depends(header_scheme)):
    user_id = await parse_user_id(authorization)
    return await get_orders(user_id)

@order_router.get("/{order_id}", response_model=MarketOrder | LimitOrder)
async def get(order_id: str, authorization: str | None = Depends(header_scheme)):
    user_id = await parse_user_id(authorization)
    return await get_order(order_id, user_id)

@order_router.delete("/{order_id}", response_model=CancelOrderResult)
async def get(order_id: str, authorization: str | None = Depends(header_scheme)):
    user_id = await parse_user_id(authorization)
    await cancel_order(user_id, order_id)
    return CancelOrderResult(success=True)

async def parse_user_id(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    
    if not authorization.startswith("Token "):
        raise HTTPException(status_code=401, detail=f"Incorrect api-key: {authorization}")
    
    token = authorization.replace("Token ", "")
    return await get_user_id(token)