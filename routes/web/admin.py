from typing import Annotated
from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.viacep import ViaCEP
from modules.brasilapi import BrasilAPI
from databases import db
from config import config
from services.cep import CEP as CEPService
from services.admin import Admin as AdminService
from services.auth import Auth as AuthService
from bootstrap import templates


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    include_in_schema = False
)

viacep = ViaCEP()
brasilapi = BrasilAPI()
cep_service = CEPService(db, viacep, brasilapi)
admin_service = AdminService(db)
auth_service = AuthService(db)



@router.get("/login", response_class=HTMLResponse)
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


@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await auth_service.login(username, password, perfil="admin")


@router.get("/logout")
async def admin_logout(request: Request):
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(config.ADMIN_COOKIE_NAME)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
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