from pydantic import BaseModel

class TransactionHistrory(BaseModel):
    ticker: str
    price: int
    amount: int
    timestamp: str
