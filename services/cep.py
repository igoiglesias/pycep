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
        cep_data = await self.repo.get_cep(cep)
        if cep_data:
            background_tasks.add_task(self.__add_to_fila_update, cep)
            return {
                "erro": False,
                "mensagem": None,
                "content": dict(cep_data)
            }

        cep_data = await self.__consultar_cep(cep)
        if cep_data.get('erro'):
            return cep_data

        cep_data['content']['cep'] = cep
        background_tasks.add_task(self.__salvar, cep_data['content'])

        return cep_data
    
    
    async def __consultar_cep(self, cep: str) -> dict:
        """
        Consulta o CEP sem cache.
        """
        cep_data = await self.viacep.consultar(cep)
        if cep_data.get('erro'):
            cep_data = await self.brasilapi.consultar_cep(cep)
        
        return cep_data
    
    
    async def __salvar(self, cep_data: dict) -> None:
        """
        Salva o CEP no banco de dados.
        """
        await self.repo.save_cep(cep_data)
    
    
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