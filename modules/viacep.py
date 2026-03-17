from config.config import VIACEP_URL
import httpx


class ViaCEP:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=60.0,
            http2=True,
            base_url=VIACEP_URL,
            limits=httpx.Limits(max_keepalive_connections=2, max_connections=6)
        )
    
    async def consultar(self, cep: str) -> dict:
        url = f"/{cep}/json/"
        try:
            response = await self.client.get(url)
        except Exception as e:
            print(f"Erro ao consultar CEP no ViaCEP({cep}): {str(e)}")
            return {
                "erro": True,
                "mensagem": "Erro ao consultar CEP",
                "content": {}
            }

        if response.status_code != 200 or response.json().get("erro"):
            return {
                "erro": True,
                "mensagem": "CEP não encontrado",
                "content": {}
            }

        return {
                "erro": False,
                "mensagem": None,
                "content": response.json()
            }