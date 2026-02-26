from config import config
from tools.token_handler import create_token


class Admin:
    def __init__(self, db):
        self.db = db
    
    
    async def login(self, username: str, password: str, response):
        """Faz login do admin."""
        admin = self.db.get_admin(username)
        if not admin or not admin['password'] == password:
            return False

        jwt_token = create_token(admin['id'])
        
        response.set_cookie(
            key="admin_auth",
            value=jwt_token,
            max_age=config.COOKIE_MAX_AGE,
            httponly=config.COOKIE_HTTPONLY,
            samesite=config.COOKIE_SAMESITE,
            secure=config.COOKIE_SECURE
        )
    
    