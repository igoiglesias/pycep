import functools
import time
from fastapi import Request



class log:
    def __init__(self, db):
        self.db = db
    
    def cep_request(self, func):
        @functools.wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            inicio = time.perf_counter()
            func_result = func(request, *args, **kwargs)
            fim = time.perf_counter()
            exec_time = (fim - inicio) * 1000
            
            data_to_log = {
                "cep": kwargs.get("cep"),
                "ip": self.__pegar_ip_real(request),
                "response_time": exec_time,
                "error": bool(request.cookies.get("error")),
                "error_message": request.cookies.get("error"),
                "user_agent": request.headers.get("user-agent"),
                "user_token": request.headers.get("authorization"),
                "user_id": None
            }

            return func_result

        return wrapper
    
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