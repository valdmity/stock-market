from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader

from src.balances.service import get_all
from src.users.service import get_user_id

balance_router = APIRouter(prefix="/balance", tags=["balance"])

header_scheme = APIKeyHeader(name="authorization", auto_error=False)

@balance_router.get("", response_model=dict[str, int])
async def get_balances(authorization: str | None = Depends(header_scheme)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Api-key is empty")
    
    if not authorization.startswith("Token "):
        raise HTTPException(status_code=401, detail=f"Incorrect api-key: {authorization}")
    
    token = authorization.replace("Token ", "")
    id = await get_user_id(token)
    return await get_all(id)