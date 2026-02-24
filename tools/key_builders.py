from typing import Optional
from fastapi import Request, Response


def cep_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    *args,
    **kwargs,
):
    cep = kwargs['args'][1]
    return f"{namespace}:{func.__qualname__}:{cep}"