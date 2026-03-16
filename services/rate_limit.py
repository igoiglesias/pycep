

import functools
import time

from fastapi_cache.decorator import cache
from fastapi import Request, HTTPException
from tools.ip import pegar_ip_real
from config import config


class RateLimit:
    def __init__(self, repo):
        self.repo = repo
        self.hits = {}


    def rate_limit(self, limit: int = 5, per: int = 60):
        def decorator(func):
                @functools.wraps(func)
                async def wrapper(request: Request, *args, **kwargs):
                    ip = pegar_ip_real(request)
                    token = request.headers.get("Authorization", "")
                    limit_pos_verify = await self._verify_token(token, limit)
                    self._rate_limit(ip, limit_pos_verify, per)

                    return await func(request, *args, **kwargs)

                return wrapper
        return decorator

    @cache(expire=config.RATE_LIMIT_EXPIRE_CACHE)
    async def _verify_token(self, token: str, limit: int) -> int:
        if token:
            token = token.replace("Bearer ", "")
            token_data = await self.repo.get_token(token)
            if token_data:
                limit = config.RATE_LIMIT_WITH_TOKEN
        return limit

    
    def _rate_limit(self, ip: str, limit: int, per: int) -> None:
        now = time.monotonic()
        
        if ip not in self.hits:
            self.hits[ip] = []

        self.hits[ip].append(now)
        
        [self.hits[ip].remove(t) for t in self.hits[ip] if t < now - per]
    
        if len(self.hits[ip]) > limit:
            raise HTTPException(status_code=429, detail="Too many requests")