from config import config
from tools.token_handler import create_token
from fastapi.responses import RedirectResponse
from tools.password import Password
from tools.session_error import set_session_error


class Admin:
    def __init__(self, db):
        self.db = db
        self.password = Password()
