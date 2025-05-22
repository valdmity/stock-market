from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader

from src.balances.service import get_all
from src.users.service import get_user_id

balance_router = APIRouter(prefix="/balance", tags=["balance"])

async def get_authorization(authorization: str | None = Header(default=None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    return authorization

@balance_router.get("", response_model=dict[str, int])
async def get_balances(authorization: str | None = Depends(get_authorization)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    
    if not authorization.startswith("TOKEN "):
        raise HTTPException(status_code=401, detail=f"Incorrect api-key: {authorization}")
    
    token = authorization.replace("TOKEN ", "")
    id = await get_user_id(token)
    return await get_all(id)