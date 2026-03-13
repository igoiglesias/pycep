import functools
import time

from fastapi import Request
from fastapi.responses import HTMLResponse
from tools.ip import pegar_ip_real


_hits = {}

def rate_limit(limit: int = 5, per: int = 60):
    def decorator(func):
            @functools.wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                ip = pegar_ip_real(request)
                now = time.monotonic()
                
                if ip not in _hits:
                    _hits[ip] = []

                _hits[ip].append(now)
                
                [_hits[ip].remove(t) for t in _hits[ip] if t < now - per]
            
                if len(_hits[ip]) > limit:
                    return HTMLResponse(content="Too Many Requests", status_code=429)

                return await func(request, *args, **kwargs)

            return wrapper
    return decorator