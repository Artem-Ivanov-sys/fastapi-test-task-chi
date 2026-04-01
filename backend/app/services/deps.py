from app.db.db import get_sessionmaker

async def get_db():
    async with get_sessionmaker()() as session:
        yield session
