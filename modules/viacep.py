import requests
from config.config import VIACEP_URL


class ViaCEP:
    def __init__(self):
        self.base_url = VIACEP_URL
    
    async def consultar(self, cep: str) -> dict:
        url = f"{self.base_url}/{cep}/json/"
        try:
            response = requests.get(url)
        except Exception as e:
            print(f"Erro ao consultar CEP({cep}): {e}")
            return {
                "erro": True,
                "mensagem": "Erro ao consultar CEP",
                "content": None
            }

        if response.status_code != 200 or response.json().get("erro"):
            return {
                "erro": True,
                "mensagem": "CEP não encontrado",
                "content": None
            }

        return {
                "erro": False,
                "mensagem": None,
                "content": response.json()
            }