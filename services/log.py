import re
import functools
import asyncio
import time
from fastapi import Request


class log:
    def __init__(self, db):
        self.db = db
    
    def cep_request(self, func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            inicio = time.perf_counter()
            kwargs['cep'] = re.sub(r"\D", "", kwargs.get("cep"))
            response = await func(request, *args, **kwargs)
            fim = time.perf_counter()
            exec_time = (fim - inicio) * 1000
            data_to_log = {
                "cep": kwargs.get("cep"),
                "ip": self.__pegar_ip_real(request),
                "response_time": exec_time,
                "error": response.get('erro'),
                "error_message": response.get('mensagem'),
                "user_agent": request.headers.get("user-agent"),
                "user_token": request.headers.get("authorization"),
                "user_id": None
            }

            asyncio.create_task(self.__log_request(data_to_log))
            asyncio.create_task(self.__incrementar_uso(kwargs.get("cep")))

            return response

        return wrapper
    
    async def __incrementar_uso(self, cep: str) -> None:
        """
        Incrementa o contador de uso do CEP.
        """
        self.db.incrementar_uso(cep)
    
    async def __log_request(self, data_to_log):
        self.db.save_request_log(**data_to_log)
    
    
    def __pegar_ip_real(self,request: Request):
        ip_forwarded = request.headers.get("X-Forwarded-For")
        ip_real = request.headers.get("X-Real-IP")

        if ip_forwarded:
            ip_cliente = ip_forwarded.split(",")[0].strip()
        elif ip_real:
            ip_cliente = ip_real
        else:
            ip_cliente = request.client.host

        return ip_cliente