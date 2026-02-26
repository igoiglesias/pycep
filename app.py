from typing import AsyncIterator, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from modules.viacep import ViaCEP
from modules.brasilapi import BrasilAPI
from tools.validators import CEP
from services.cep import CEP as CEPService
from services.admin import Admin as AdminService
from databases import db
from config.config import CACHE_PREFIX, CACHE_ENABLE


db.initialize_db()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix=CACHE_PREFIX, enable=CACHE_ENABLE)
    yield

app = FastAPI(
    title="PyCEP",
    description="API wrapper do ViaCEP para consulta de CEP.",
    version="0.0.1",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

viacep = ViaCEP()
brasilapi = BrasilAPI()
cep_service = CEPService(db, viacep, brasilapi)
admin_service = AdminService(db)


@app.get("/", response_class=HTMLResponse, tags=["Index"])
async def index(request: Request):
    return templates.TemplateResponse("pages/index.html", {"request": request, "title": "PyCEP"})


@app.get("/cep/{cep}", tags=["Api"])
async def consulta_cep(cep: CEP, background_tasks: BackgroundTasks):
    background_tasks.add_task(cep_service.incrementar_uso, cep)
    return await cep_service.consultar(cep, background_tasks)


@app.get("/admin/login", response_class=HTMLResponse, tags=["Admin"])
async def admin_login(request: Request):
    return templates.TemplateResponse("pages/admin/login.html", {"request": request, "title": "Admin Login"})


@app.post("/admin/login/")
async def login( response: Response ,username: Annotated[str, Form()], password: Annotated[str, Form()]):
    await admin_service.login(username, password, response)


@app.get("/admin/dashboard", response_class=HTMLResponse, tags=["Admin"])
async def admin_dashboard(request: Request):
    dashboard_data = await cep_service.get_dashboard()
    return templates.TemplateResponse(
        "pages/admin/dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "total_consultas": dashboard_data['total_consultas'],
            "top_ceps": dashboard_data['top_ceps']
        }
    )