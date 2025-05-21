from fastapi import FastAPI

from src.routers.public import public_router
from src.routers.admin import admin_router
from src.routers.balance import balance_router
from src.routers.order import order_router


app = FastAPI()
base_prefix = "/api/v1"
app.include_router(public_router, prefix=base_prefix)
app.include_router(admin_router, prefix=base_prefix)
app.include_router(balance_router, prefix=base_prefix)
app.include_router(order_router, prefix=base_prefix)
