from typing import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from databases.db import DB
from config import config
from databases.repository import Repository
from services.rate_limit import RateLimit
from tools.jinja_filters import format_error_messages


db = DB(config.DB_PATH)

def get_db():
    return db

repo = Repository(get_db)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix=config.CACHE_PREFIX, enable=config.CACHE_ENABLE)
    await db.connect()
    await repo.initialize_db()
    yield
    await db.disconnect()

app = FastAPI(
    title="PyCEP",
    description="API wrapper do ViaCEP para consulta de CEP.",
    version="0.0.1",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        if request.url.path.endswith((".woff2", ".min.css", ".min.js")):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            response.headers["Cache-Control"] = "public, max-age=86400"
    return response
templates = Jinja2Templates(directory="templates")
templates.env.filters["format_error"] = format_error_messages

rate_limiter = RateLimit(repo)