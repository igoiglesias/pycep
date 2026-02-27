from config import config
from tools.token_handler import create_token
from fastapi.responses import RedirectResponse
from tools.password import Password


class Admin:
    def __init__(self, db):
        self.db = db
        self.password = Password()
    
    
    async def login(self, username: str, password: str):
        """Faz login do admin."""
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        admin = self.db.get_admin(username)
        if not admin or not self.password.verify(password, admin['password']):
            response.headers['location'] = "/admin/login"
            return response

        jwt_token = create_token(admin['id'])
        
        response.set_cookie(
            key=config.COOKIE_NAME,
            domain=config.COOKIE_DOMAIN,
            value=jwt_token,
            max_age=config.COOKIE_MAX_AGE * 60,
            httponly=config.COOKIE_HTTPONLY,
            samesite=config.COOKIE_SAMESITE,
            secure=config.COOKIE_SECURE
        )
        return response