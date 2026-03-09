from fastapi_cache.decorator import cache
from config.config import CACHE_EXPIRE, TENTATIVAS_TO_UPDATE
from tools.key_builders import cep_key_builder


class CEP:
    def __init__(self, db, viacep, brasilapi):
        self.db = db
        self.viacep = viacep
        self.brasilapi = brasilapi


    async def get_dashboard(self) -> dict:
        """
        Retorna os dados do dashboard.
        """
        total_consultas = await self.db.get_total_consultas()
        top_ceps = await self.db.get_top_ceps()
        return {
            "total_consultas": total_consultas,
            "top_ceps": top_ceps
        }


    @cache(expire=CACHE_EXPIRE, key_builder=cep_key_builder)
    async def consultar(self, cep: str, background_tasks) -> dict:
        """
        Consulta o CEP.
        """
        cep_data = await self.db.get_cep(cep)
        if cep_data:
            background_tasks.add_task(self.__add_to_fila_update, cep)
            return {
                "erro": False,
                "mensagem": None,
                "content": dict(cep_data)
            }

        cep_data = await self.viacep.consultar(cep)
        if cep_data.get('erro'):
            cep_data = await self.brasilapi.consultar_cep(cep)
            if cep_data.get('erro'):
                return cep_data

        cep_data['content']['cep'] = cep
        background_tasks.add_task(self.__salvar, cep_data['content'])

        return cep_data
    
    
    async def __salvar(self, cep_data: dict) -> None:
        """
        Salva o CEP no banco de dados.
        """
        await self.db.save_cep(cep_data)
    
    
    async def __add_to_fila_update(self, cep: str) -> None:
        """
        Atualiza o CEP no banco de dados.
        """
        if not await self.db.has_to_update(cep):
            return

        await self.db.add_to_fila_update(cep)


    async def update_cep(self, cep: str) -> dict:
        """Atualiza o CEP no banco de dados.
        """
        cep_data = await self.viacep.consultar(cep)
        if cep_data.get('erro'):
            return cep_data

        cep_data['content']['cep'] = cep
        await self.db.update_cep(cep_data['content'])

        return cep_data
    
    async def processar_fila_update(self) -> None:
        """Processa a fila de atualização de CEPs.
        """
        ceps = await self.db.get_fila_update()
        for cep in ceps:
            cep_data = await self.update_cep(cep['cep'])
            if not cep_data['erro']:
                await self.db.remove_from_fila_update(cep['cep'])
                continue
            
            await self.__increment_update_attempts(cep)
    
    async def __increment_update_attempts(self, cep: dict) -> None:
        """Incrementa o número de tentativas de atualização de um CEP.
        """        
        if cep['tentativas'] >= TENTATIVAS_TO_UPDATE:
            await self.db.set_error_fila_update(cep['cep'])

        await self.db.increment_update_attempts(cep['cep'])