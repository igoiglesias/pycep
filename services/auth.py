import functools
from fastapi import Request
from fastapi.responses import RedirectResponse
from config import config
from tools.token_handler import decode_token, create_token
from tools.session_error import set_session_error
from tools.password import Password



class Auth:
    def __init__(self, db):
        self.db = db
        self.password = Password()

    def verify(self, perfil="user"):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                url = '/'
                cookie_name = config.USER_COOKIE_NAME
                if perfil == "admin":
                    url = "/admin/"
                    cookie_name = config.ADMIN_COOKIE_NAME
                
                response = RedirectResponse(url=f"{url}login", status_code=302)
                jwt_token = request.cookies.get(cookie_name)
                if not jwt_token:
                    set_session_error(response, "Sessão expirada")
                    return response

                decoded_token = decode_token(jwt_token)
                if not decoded_token:
                    set_session_error(response, "Token inválido")
                    return response

                user = await self.db.get_user_by_id(decoded_token.get("sub"))
                if perfil == "admin":
                    user = await self.db.get_user_by_id(decoded_token.get("sub"))
                
                if not user:
                    response.delete_cookie(cookie_name)
                    set_session_error(response, "Usuário não encontrado")
                    return response

                request.state.user = {
                    'id': user['id'],
                    'name': user['name'].split(" ")[0],
                    'email': user['email'],
                }

                return await func(request, *args, **kwargs)
            return wrapper
        return decorator


    async def login(self, username: str, password: str, perfil: str = "user"):
        """Faz login do Usuário."""
        url = '/'
        cookie_name = config.USER_COOKIE_NAME
        user = await self.db.get_user(username)

        if perfil == "admin":
            url = "/admin/"
            cookie_name = config.ADMIN_COOKIE_NAME
            user = await self.db.get_admin(username)

        response = RedirectResponse(url=f"{url}dashboard", status_code=302)
        if not user or not self.password.verify(password, user['password']):
            response.headers['location'] = f"{url}login"
            set_session_error(response, "Credenciais inválidas")
            return response

        jwt_token = create_token(user['id'])
        
        response.set_cookie(
            key=cookie_name,
            domain=config.COOKIE_DOMAIN,
            value=jwt_token,
            max_age=config.COOKIE_MAX_AGE * 60,
            httponly=config.COOKIE_HTTPONLY,
            samesite=config.COOKIE_SAMESITE,
            secure=config.COOKIE_SECURE
        )
        return response