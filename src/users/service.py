from fastapi import HTTPException
from secrets import token_hex
from sqlalchemy import insert, select, and_, update
from uuid import uuid4
from hashlib import sha256
import hmac

from src.config import settings
from src.database import session_factory
from src.users.models import User
from src.users.schemas import UserCreate, UserModel, Role
from src.crypto import fernet


async def create_user(user: UserCreate) -> UserModel:
    api_key = token_hex(32)
    encoded_api_key = api_key.encode()
    hash = hmac.new(settings.HASH_KEY.encode(), encoded_api_key, sha256).hexdigest()
    encrypted = fernet.encrypt(encoded_api_key).decode()
    
    users = User.__table__
    query = insert(users).values(
        id=uuid4(),
        name=user.name,
        role=Role.USER,
        api_key_hash=hash,
        encrypted_api_key=encrypted
    ).returning(users.c.id, users.c.name, users.c.role)
    
    try:
        async with session_factory() as session:
            result = await session.execute(query)
            entity = result.one()
            await session.commit()
            return UserModel(
                id=str(entity.id),
                name=entity.name,
                role=entity.role,
                api_key=api_key
            )
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="User with this name already exists")
        raise e

async def is_user_admin(api_key: str) -> bool:
    hash = hmac.new(settings.HASH_KEY.encode(), api_key.encode(), sha256).hexdigest()
    query = select(User.role).where(and_(User.api_key_hash == hash, User.is_active == True))

    async with session_factory() as session:
        result = await session.execute(query)
        entity = result.one_or_none()
        if not entity:
            raise HTTPException(status_code=401, detail="Incorrect api-key")
        return str(entity.role) == "Role.ADMIN" # todo: костыль, при сравнении с enum был false

async def get_user_id(api_key: str) -> str:
    hash = hmac.new(settings.HASH_KEY.encode(), api_key.encode(), sha256).hexdigest()
    query = select(User.id).where(and_(User.api_key_hash == hash, User.is_active == True))

    async with session_factory() as session:
        result = await session.execute(query)
        entity = result.one_or_none()
        if not entity:
            raise HTTPException(status_code=401, detail="Incorrect api-key")
        return str(entity.id)

async def delete_user(user_id: str) -> UserModel:
    stmt = update(User).where(User.id == user_id).values(is_active=False).returning(User.id, User.name, User.role, User.encrypted_api_key)
    async with session_factory() as session:
        result = await session.execute(stmt)
        entity = result.one()
        await session.commit()
        if not entity:
            raise HTTPException(status_code=404, detail="user not found")
        return UserModel(
            id=str(entity.id),
            name=entity.name,
            role=entity.role,
            api_key=fernet.decrypt(entity.encrypted_api_key).decode()
        )
