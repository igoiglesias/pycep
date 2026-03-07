from typing import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# from databases import db
from databases.db import DB
from config import config

DATABASE = None

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix=config.CACHE_PREFIX, enable=config.CACHE_ENABLE)
    db = DB(config.DB_PATH)
    # await db.initialize_db()
    await db.connect()
    global DATABASE
    DATABASE = db
    yield
    await DATABASE.disconnect()

app = FastAPI(
    title="PyCEP",
    description="API wrapper do ViaCEP para consulta de CEP.",
    version="0.0.1",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")