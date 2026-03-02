from config import config
from tools.token_handler import create_token
from fastapi.responses import RedirectResponse
from tools.password import Password
from tools.session_error import set_session_error


class User:
    def __init__(self, db):
        self.db = db
        self.password = Password()
    
    
    async def login(self, username: str, password: str):
        """Faz login do Usuário."""
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        admin = self.db.get_admin(username)
        if not admin or not self.password.verify(password, admin['password']):
            response.headers['location'] = "/admin/login"
            set_session_error(response, "Credenciais inválidas")
            return response

        jwt_token = create_token(admin['id'])
        
        response.set_cookie(
            key=config.ADMIN_COOKIE_NAME,
            domain=config.ADMIN_COOKIE_DOMAIN,
            value=jwt_token,
            max_age=config.ADMIN_COOKIE_MAX_AGE * 60,
            httponly=config.ADMIN_COOKIE_HTTPONLY,
            samesite=config.ADMIN_COOKIE_SAMESITE,
            secure=config.ADMIN_COOKIE_SECURE
        )
        return response