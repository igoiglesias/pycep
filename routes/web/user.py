from typing import Annotated

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from services.auth import Auth as AuthService
from services.user import User as UserService
from bootstrap import templates, get_db
from databases.repository import Repository
from config import config
from tools.rate_limit import rate_limit


router = APIRouter(
    tags=["Index"],
    include_in_schema = False
)

repo = Repository(get_db)

auth_service = AuthService(repo)
user_service = UserService(repo)


@router.get("/", response_class=HTMLResponse)
@rate_limit(limit=50, per=60)
async def index(request: Request):
    return templates.TemplateResponse("pages/index.html", {"request": request, "title": "PyCEP"})


@router.get("/dashboard", response_class=HTMLResponse)
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


@router.get("/user/create", response_class=HTMLResponse)
async def user_create(request: Request):
    return templates.TemplateResponse(
        "pages/create_user.html", 
        {
            "request": request,
            "error": request.cookies.get("error"),
            "title": "Criar Usuário"
        }
    )


@router.post("/user/create")
async def user_post_create(name: str = Form(default=None), email: str = Form(default=None), password: str = Form(default=None)):
    return await user_service.create(name, email, password)


@router.get("/user/token", response_class=HTMLResponse)
@auth_service.verify(perfil="user")
async def user_token(request: Request):
    user = request.state.user
    tokens = await user_service.get_tokens(user['id'])
    return templates.TemplateResponse(
        "pages/token_user.html", 
        {
            "request": request,
            "tokens": tokens,
            "title": "Listar Tokens"
        }
    )


@router.get("/user/token/create", response_class=HTMLResponse)
@auth_service.verify(perfil="user")
async def user_token_create(request: Request):
    return templates.TemplateResponse(
        "pages/token_user_create.html", 
        {
            "request": request,
            "error": request.cookies.get("error"),
            "title": "Criar Token"
        }
    )


@router.post("/user/token/create")
@auth_service.verify(perfil="user")
async def user_post_token_create(request: Request, name: str = Form(default=None)):
    user = request.state.user
    return await user_service.create_token(user['id'], name)


@router.post("/user/token/delete/{token_id}")
@auth_service.verify(perfil="user")
async def user_token_delete(request: Request, token_id: int):
    user = request.state.user
    return await user_service.delete_token(user['id'], token_id)