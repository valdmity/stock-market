from uuid import uuid4
from sqlalchemy import insert, update, select, desc
from sqlalchemy.sql import or_
from fastapi import HTTPException

from src.database import session_factory
from src.orders.models import Order, Status, Direction
from src.instruments.models import Instrument
from src.transactions.models import Transaction
from src.orders.schemas import LimitOrderBody, MarketOrderBody, MarketOrder, LimitOrder, OrderBookItem, OrderBook


# async def create_order(user_id: str, order: LimitOrderBody | MarketOrderBody) -> str:
#     query = select(Instrument.id).where(Instrument.ticker == order.ticker)
#     async with session_factory() as session:
#         query_result = await session.execute(query)
#         instrument_id = query_result.one().id
#         stmt = insert(Order).values(
#             id=uuid4(),
#             user_id=user_id,
#             instrument_id=instrument_id,
#             direction=order.direction,
#             qty=order.qty,
#             price=(None if isinstance(order, MarketOrderBody) else order.price),
#             filled=(None if isinstance(order, MarketOrderBody) else 0)
#         ).returning(Instrument.id)
#         stmt_result = await session.execute(stmt)
#         order_id = stmt_result.one().id
#         await session.commit()
#         return order_id

async def create_order(user_id: str, order: LimitOrderBody | MarketOrderBody) -> str:
    async with session_factory() as session:
        query = select(Instrument.id).where(Instrument.ticker == order.ticker)
        instrument_id = (await session.execute(query)).one().id
        order_id = uuid4()
        stmt = insert(Order).values(
            id=order_id,
            user_id=user_id,
            instrument_id=instrument_id,
            direction=order.direction,
            qty=order.qty,
            price=(None if isinstance(order, MarketOrderBody) else order.price),
            filled=(None if isinstance(order, MarketOrderBody) else 0)
        ).returning(Order.id)
        await session.execute(stmt)
            
        opposite_dir = Direction.SELL if order.direction == Direction.BUY else Direction.BUY
        price_condition = (Order.price <= order.price if isinstance(order, LimitOrderBody) and order.direction == Direction.BUY 
            else Order.price >= order.price if isinstance(order, LimitOrderBody) else True)
        match_query = select(Order).where(
            Order.instrument_id == instrument_id,
            Order.direction == opposite_dir,
            Order.status.in_([Status.NEW, Status.PARTIALLY_EXECUTED]),
            price_condition
        ).with_for_update()
        matches = (await session.execute(match_query)).all()
            
        qty_left = order.qty
        for match in sorted(matches, key=lambda x: (x.price, x.timestamp)):
            if qty_left <= 0:
                break
            fill_qty = min(qty_left, match.qty - (match.filled or 0))
            if fill_qty > 0:
                await session.execute(
                    update(Order).where(Order.id == match.id).values(
                        filled=(match.filled or 0) + fill_qty,
                        status=Status.EXECUTED if (match.filled or 0) + fill_qty == match.qty else Status.PARTIALLY_EXECUTED
                    )
                )
                await session.execute(
                    insert(Transaction).values(
                        id=uuid4(),
                        instrument_id=instrument_id,
                        amount=fill_qty,
                        price=match.price
                    )
                )
                qty_left -= fill_qty
            
        new_status = Status.EXECUTED if qty_left == 0 else Status.PARTIALLY_EXECUTED if qty_left < order.qty else Status.NEW
        await session.execute(
            update(Order).where(Order.id == order_id).values(
                filled=order.qty - qty_left if isinstance(order, LimitOrderBody) else None,
                status=new_status
            )
        )
        await session.commit()
        return str(order_id)

async def cancel_order(user_id: str, order_id: str):
    stmt = update(Order).where(
        Order.id == order_id,
        Order.user_id == user_id,
        or_(Order.status == Status.NEW, Order.status == Status.PARTIALLY_EXECUTED)
    ).values(status=Status.CANCELLED)
    async with session_factory() as session:
        await session.execute(stmt)
        await session.commit()

async def get_order(id: str, user_id: str) -> MarketOrder | LimitOrder:
    query = select(
        Order.id,
        Order.status,
        Order.user_id,
        Order.timestamp,
        Order.direction,
        Instrument.ticker,
        Order.price,
        Order.qty,
        Order.filled
    ).select_from(
        Order
    ).join(
        Instrument,
        Instrument.id == Order.instrument_id
    ).where(
        Order.id == id,
        Order.user_id == user_id
    )
    async with session_factory() as session:
        result = await session.execute(query)
        order = result.one_or_none()
        if not order:
            raise HTTPException(status_code=404)
        return MarketOrder(
            id=order.id,
            status = order.status,
            user_id=order.user_id,
            timestamp=order.timestamp,
            body=MarketOrderBody(
                direction=order.direction,
                qty=order.qty,
                ticker=order.ticker
            )
        ) if not order.price else LimitOrder(
            id=order.id,
            status = order.status,
            user_id=order.user_id,
            timestamp=order.timestamp,
            filled=order.filled,
            body=LimitOrderBody(
                direction=order.direction,
                qty=order.qty,
                ticker=order.ticker,
                price=order.price
            )
        )

async def get_orders(user_id: str) -> list[MarketOrder | LimitOrder]:
    query = select(
        Order.id,
        Order.status,
        Order.user_id,
        Order.timestamp,
        Order.direction,
        Instrument.ticker,
        Order.price,
        Order.qty,
        Order.filled
    ).select_from(
        Order
    ).join(
        Instrument,
        Instrument.id == Order.instrument_id
    ).where(
        Order.user_id == user_id
    )
    async with session_factory() as session:
        result = await session.execute(query)
        orders = result.all()
        return [
            MarketOrder(
                id=order.id,
                status = order.status,
                user_id=order.user_id,
                timestamp=order.timestamp,
                body=MarketOrderBody(
                    direction=order.direction,
                    qty=order.qty,
                    ticker=order.ticker
                )
            ) if not order.price else LimitOrder(
                id=order.id,
                status = order.status,
                user_id=order.user_id,
                timestamp=order.timestamp,
                filled=order.filled,
                body=LimitOrderBody(
                    direction=order.direction,
                    qty=order.qty,
                    ticker=order.ticker,
                    price=order.price
                )
            ) for order in orders
        ]

async def get_orderbook(ticker: str, limit: int):
    bid_query = select(
        Order.price,
        Order.qty,
        Order.filled
    ).select_from(
        Order
    ).join(
        Instrument,
        Instrument.id == Order.instrument_id
    ).where(
        Instrument.ticker == ticker,
        Order.price != None,
        Order.direction == Direction.BUY,
        or_(Order.status == Status.NEW, Order.status == Status.PARTIALLY_EXECUTED)
    ).order_by(
        desc(Order.price)
    ).limit(
        limit
    )
    ask_query = select(
        Order.price,
        Order.qty,
        Order.filled
    ).select_from(
        Order
    ).join(
        Instrument,
        Instrument.id == Order.instrument_id
    ).where(
        Instrument.ticker == ticker,
        Order.price != None,
        Order.direction == Direction.SELL,
        or_(Order.status == Status.NEW, Order.status == Status.PARTIALLY_EXECUTED)
    ).order_by(
        Order.price
    ).limit(
        limit
    )
    async with session_factory() as session:
        bid_result = await session.execute(bid_query)
        ask_result = await session.execute(ask_query)
        bid_levels = [OrderBookItem(price=bl.price, qty=(bl.qty-bl.filled)) for bl in bid_result.all()]
        ask_levels = [OrderBookItem(price=al.price, qty=(al.qty-al.filled)) for al in ask_result.all()]
        return OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)
