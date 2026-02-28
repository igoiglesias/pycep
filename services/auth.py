import functools
from fastapi import Request
from fastapi.responses import RedirectResponse
from config import config
from tools.token_handler import decode_token
from tools.session_error import set_session_error


class Auth:
    def __init__(self, db):
        self.db = db


    def verify_admin(self, func) -> bool:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            response = RedirectResponse(url="/admin/login", status_code=302)
            jwt_token = request.cookies.get(config.COOKIE_NAME)
            if not jwt_token:
                set_session_error(response, "Sessão expirada")
                return response

            decoded_token = decode_token(jwt_token)
            if not decoded_token:
                set_session_error(response, "Token inválido")
                return response
            
            user = self.db.get_admin_by_id(decoded_token.get("sub"))
            if not user:
                response.delete_cookie(config.COOKIE_NAME)
                set_session_error(response, "Usuário não encontrado")
                return response

            request.state.user = {
                'id': user['id'],
                'name': user['name'].split(" ")[0],
                'email': user['email'],
            }

            return await func(request, *args, **kwargs)
        return wrapper