from fastapi.responses import RedirectResponse


def set_session_error(response, error: str) -> RedirectResponse:
    response.set_cookie("error", error, expires=1)
    return response