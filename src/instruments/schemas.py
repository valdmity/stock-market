from pydantic import BaseModel

class CreateInstrument(BaseModel):
    name: str
    ticker: str

class InstrumentModel(BaseModel):
    name: str
    ticker: str
