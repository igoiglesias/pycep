import functools
from config import config
from fastapi.responses import RedirectResponse
from tools.token_handler import decode_token


def auth(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = RedirectResponse(url="/admin/login", status_code=302)
        cookies = kwargs['request'].cookies
        if config.COOKIE_NAME not in cookies:
            return response

        jwt_token = cookies[config.COOKIE_NAME]
        decoded_token = decode_token(jwt_token)
        if not decoded_token:
            return response

        return await func(*args, **kwargs)
    return wrapper