from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy import inspect
from dotenv import load_dotenv
from os import getenv
# from asyncio import run as arun

# from app.models.models import User
from app.models.models import Base

load_dotenv()
db_user = getenv("POSTGRES_USER", "testuser")
db_pass = getenv("POSTGRES_PASSWORD", "qwertyuiop")
db_name = getenv("POSTGRES_DB", "testdb")

_engine = None
_sessionmaker = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            f"postgresql+asyncpg://{db_user}:{db_pass}@db_postgres:5432/{db_name}"
        )
    return _engine

def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _sessionmaker

async def create_table_if_not_exist():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# AsyncSessionLocal = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
