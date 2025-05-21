from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserCreate(BaseModel):
    name: str

class UserModel(BaseModel):
    id: str
    name: str
    role: Role
    api_key: str
