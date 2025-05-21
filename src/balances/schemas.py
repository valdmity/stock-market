from pydantic import BaseModel

class Balance(BaseModel):
    user_id: str
    ticker: str
    amount: int
