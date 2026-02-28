

def set_session_error(response, error: str):
    response.set_cookie("error", error, expires=0)
    return response