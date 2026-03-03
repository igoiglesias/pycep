from typing import AsyncIterator, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from modules.viacep import ViaCEP
from modules.brasilapi import BrasilAPI
from tools.validators import CEP, CEP_RESPONSE
from databases import db
from config import config
from services.cep import CEP as CEPService
from services.admin import Admin as AdminService
from services.user import User as UserService
from services.auth import Auth as AuthService
from services.log import log as LogService



db.initialize_db()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix=config.CACHE_PREFIX, enable=config.CACHE_ENABLE)
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
user_service = UserService(db)
auth_service = AuthService(db)
log_service = LogService(db)



@app.get("/", response_class=HTMLResponse, include_in_schema=False, tags=["Index"])
async def index(request: Request):
    return templates.TemplateResponse("pages/index.html", {"request": request, "title": "PyCEP"})


@app.get("/dashboard", include_in_schema=False, tags=["Index"])
@auth_service.verify(perfil="user")
async def user_dashboard(request: Request):
    return templates.TemplateResponse(
        "pages/dashboard.html", 
        {
            "request": request,
            "title": "Dashboard"
        }
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False, tags=["Index"])
async def user_login(request: Request):
    error = request.cookies.get("error")
    return templates.TemplateResponse(
        "pages/login.html", 
        {
            "request": request,
            "title": "Login", 
            "error": error
        }
    )


@app.post("/login", include_in_schema=False, tags=["Index"])
async def user_post_login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await auth_service.login(username, password, perfil="user")


@app.get("/logout", include_in_schema=False, tags=["Index"])
async def user_logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(config.USER_COOKIE_NAME)
    return response


@app.get("/cep/{cep}", response_model=CEP_RESPONSE, tags=["Api"])
@log_service.cep_request
async def consulta_cep(request: Request, cep: CEP, background_tasks: BackgroundTasks):
    """
    Consulta o CEP informado
    """
    return await cep_service.consultar(cep, background_tasks)


@app.get("/admin/login", response_class=HTMLResponse, include_in_schema=False, tags=["Admin"])
async def admin_login(request: Request):
    error = request.cookies.get("error")
    return templates.TemplateResponse(
        "pages/admin/login.html", 
        {
            "request": request,
            "title": "Admin Login", 
            "error": error
        }
    )


@app.post("/admin/login/", include_in_schema=False, tags=["Admin"])
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await auth_service.login(username, password, perfil="admin")


@app.get("/admin/logout", include_in_schema=False, tags=["Admin"])
async def admin_logout(request: Request):
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(config.ADMIN_COOKIE_NAME)
    return response


@app.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False, tags=["Admin"])
@auth_service.verify(perfil="admin")
async def admin_dashboard(request: Request):
    user = request.state.user
    dashboard_data = await cep_service.get_dashboard()
    return templates.TemplateResponse(
        "pages/admin/dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "total_consultas": dashboard_data['total_consultas'],
            "top_ceps": dashboard_data['top_ceps'],
            "user": user
        }
    )
