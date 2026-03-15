import re
import functools
import time

import asyncio
from fastapi import Request

from tools.ip import pegar_ip_real
from tools.validators import CEP_PATTERN


class log:
    def __init__(self, repo):
        self.repo = repo
    
    def cep_request(self, func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            inicio = time.perf_counter()
            kwargs['cep'] = CEP_PATTERN.sub("", kwargs.get("cep", ""))
            response = await func(request, *args, **kwargs)
            fim = time.perf_counter()
            exec_time = (fim - inicio) * 1000
            data_to_log = {
                "cep": kwargs.get("cep"),
                "ip": pegar_ip_real(request),
                "response_time": exec_time,
                "error": response.get('erro'),
                "error_message": response.get('mensagem'),
                "user_agent": request.headers.get("user-agent"),
                "user_token": request.headers.get("authorization"),
                "user_id": None
            }

            asyncio.create_task(self.__log_request(data_to_log))

            return response

        return wrapper

    async def __log_request(self, data_to_log):
        await self.repo.save_request_log(**data_to_log)
