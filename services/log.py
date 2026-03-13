import re
import functools
import time

import asyncio
from fastapi import Request

from tools.ip import pegar_ip_real


class log:
    def __init__(self, repo):
        self.repo = repo
    
    def cep_request(self, func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            inicio = time.perf_counter()
            cep = kwargs.get("cep", "")
            kwargs['cep'] = re.sub(r"\D", "", cep)
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
            asyncio.create_task(self.__incrementar_uso(cep))

            return response

        return wrapper
    
    async def __incrementar_uso(self, cep: str) -> None:
        """
        Incrementa o contador de uso do CEP.
        """
        await self.repo.incrementar_uso(cep)
    
    async def __log_request(self, data_to_log):
        await self.repo.save_request_log(**data_to_log)
