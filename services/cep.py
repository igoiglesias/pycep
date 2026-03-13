from fastapi_cache.decorator import cache
from config.config import CACHE_EXPIRE, TENTATIVAS_TO_UPDATE
from tools.key_builders import cep_key_builder


class CEP:
    def __init__(self, repo, viacep, brasilapi):
        self.repo = repo
        self.viacep = viacep
        self.brasilapi = brasilapi


    @cache(expire=CACHE_EXPIRE, key_builder=cep_key_builder)
    async def consultar(self, cep: str, background_tasks) -> dict:
        """
        Consulta o CEP.
        """
        cep_data = await self.__get_cep(cep)

        if "has_to_save" not in cep_data:
            background_tasks.add_task(self.__salvar, cep_data.copy(), cep)
            cep_data.pop("has_to_save", None)

        background_tasks.add_task(self.__add_to_fila_update, cep)

        return cep_data


    async def __get_cep(self, cep: str) -> dict:
        cep_data = await self.repo.get_cep(cep)
        if not cep_data:
            cep_data = await self.__consultar_cep(cep)
            if cep_data['erro']:
                cep_data['content'] = None
            return cep_data

        elif cep_data['existe'] == 0:
            return {
                "erro": True,
                "mensagem": "CEP não encontrado",
                "content": None,
                "has_to_save": False
            }

        return {
            "erro": False,
            "mensagem": "CEP encontrado",
            "content": {
                "cep": cep_data['cep'],
                "logradouro": cep_data['logradouro'],
                "complemento": cep_data['complemento'],
                "bairro": cep_data['bairro'],
                "localidade": cep_data['localidade'],
                "uf": cep_data['uf'],
                "ibge": cep_data['ibge'],
                "gia": cep_data['gia'],
                "ddd": cep_data['ddd'],
                "siafi": cep_data['siafi']
            },
            "has_to_save": False
        }


    async def __consultar_cep(self, cep: str) -> dict:
        """
        Consulta o CEP sem cache.
        """
        cep_data = await self.viacep.consultar(cep)
        if cep_data.get('erro'):
            cep_data = await self.brasilapi.consultar_cep(cep)
        
        return cep_data
    
    
    async def __salvar(self, cep_data: dict, cep: str) -> None:
        """
        Salva o CEP no banco de dados.
        """
        if cep_data.get('erro'):
            cep_data['content'] = {
                "cep": cep,
                "logradouro": None,
                "complemento": None,
                "bairro": None,
                "localidade": None,
                "uf": None,
                "ibge": None,
                "gia": None,
                "ddd": None,
                "siafi": None
            }
        await self.repo.save_cep(cep_data, cep)
    
    
    async def __add_to_fila_update(self, cep: str) -> None:
        """
        Atualiza o CEP no banco de dados.
        """
        if not await self.repo.has_to_update(cep):
            return

        await self.repo.add_to_fila_update(cep)


    async def update_cep(self, cep: str) -> dict:
        """Atualiza o CEP no banco de dados.
        """
        cep_data = await self.__consultar_cep(cep)
        if cep_data.get('erro'):
            return cep_data

        cep_data['content']['cep'] = cep
        await self.repo.update_cep(cep_data['content'])

        return cep_data
    
    async def processar_fila_update(self) -> None:
        """Processa a fila de atualização de CEPs.
        """
        ceps = await self.repo.get_fila_update()
        for cep in ceps:
            cep_data = await self.update_cep(cep['cep'])
            if not cep_data['erro']:
                await self.repo.remove_from_fila_update(cep['cep'])
                continue
            
            await self.__increment_update_attempts(cep)
    
    async def __increment_update_attempts(self, cep: dict) -> None:
        """Incrementa o número de tentativas de atualização de um CEP.
        """        
        if cep['tentativas'] >= TENTATIVAS_TO_UPDATE:
            await self.repo.set_error_fila_update(cep['cep'])

        await self.repo.increment_update_attempts(cep['cep'])