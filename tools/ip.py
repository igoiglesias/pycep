from fastapi import Request


def pegar_ip_real(request: Request):
        ip_forwarded = request.headers.get("X-Forwarded-For")
        ip_real = request.headers.get("X-Real-IP")

        if ip_forwarded:
            ip_cliente = ip_forwarded.split(",")[0].strip()
        elif ip_real:
            ip_cliente = ip_real
        else:
            ip_cliente = request.client.host # type: ignore

        return ip_cliente