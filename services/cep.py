import re
from fastapi_cache.decorator import cache
from config.config import CACHE_EXPIRE
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
        total_consultas = self.db.get_total_consultas()
        top_ceps = self.db.get_top_ceps()
        return {
            "total_consultas": total_consultas,
            "top_ceps": top_ceps
        }


    @cache(expire=CACHE_EXPIRE, key_builder=cep_key_builder)
    async def consultar(self, cep: str, background_tasks) -> dict:
        """
        Consulta o CEP.
        """
        cep = re.sub(r"\D", "", cep)

        cep_data = self.db.get_cep(cep)
        if cep_data:
            background_tasks.add_task(self.__atualizar, cep)
            return {
                "erro": False,
                "mensagem": None,
                "content": cep_data
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
        self.db.save_cep(cep_data)
    
    
    async def __atualizar(self, cep: str) -> None:
        """
        Atualiza o CEP no banco de dados.
        """
        if not self.db.has_to_update(cep):
            return

        cep_data = await self.viacep.consultar(cep)
        if cep_data.get('erro'):
            return

        cep_data['content']['cep'] = cep
        self.db.update_cep(cep_data['content'])
        