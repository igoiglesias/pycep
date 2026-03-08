from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from services.auth import Auth as AuthService
from bootstrap import templates, get_db
from databases.repository import Repository
from config import config


router = APIRouter(
    tags=["Index"],
    include_in_schema = False
)

repo = Repository(get_db)

auth_service = AuthService(repo)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("pages/index.html", {"request": request, "title": "PyCEP"})


@router.get("/dashboard")
@auth_service.verify(perfil="user")
async def user_dashboard(request: Request):
    return templates.TemplateResponse(
        "pages/dashboard.html", 
        {
            "request": request,
            "title": "Dashboard"
        }
    )


@router.get("/login", response_class=HTMLResponse)
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


@router.post("/login")
async def user_post_login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await auth_service.login(username, password, perfil="user")


@router.get("/logout")
async def user_logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(config.USER_COOKIE_NAME)
    return response