from fastapi import FastAPI

from contextlib import asynccontextmanager

from app.db.db import create_table_if_not_exist
from app.api.api import ROUTERS

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table_if_not_exist()
    yield

app = FastAPI(lifespan=lifespan)
for router in ROUTERS:
    app.include_router(router)
