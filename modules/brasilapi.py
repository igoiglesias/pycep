import requests
from config.config import BRASILAPI_URL


class BrasilAPI:
    def __init__(self):
        self.base_url = BRASILAPI_URL
        self.states = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }

    async def consultar_cep(self, cep: str) -> dict:
        url = f"{self.base_url}/cep/v2/{cep}"
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

        data = response.json()
        return {
                "erro": False,
                "mensagem": None,
                "content": {
                    "cep": data.get("cep", ""),
                    "logradouro": data.get("street", ""),
                    "complemento": "",
                    "unidade": "",
                    "bairro": data.get("neighborhood", ""),
                    "localidade": data.get("city", ""),
                    "uf": data.get("state", ""),
                    "estado": self.states.get(data.get("state"), ""),
                    "regiao": data.get("region", ""),
                    "ibge": data.get("ibge", ""),
                    "gia": data.get("gia", ""),
                    "ddd": data.get("ddd", ""),
                    "siafi": data.get("siafi", "")
                }
            }