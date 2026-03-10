

class Admin:
    def __init__(self, repo):
        self.repo = repo
    
    async def get_dashboard(self) -> dict:
        """
        Retorna os dados do dashboard.
        """
        total_consultas = await self.repo.get_total_consultas()
        top_ceps = await self.repo.get_top_ceps()
        return {
            "total_consultas": total_consultas,
            "top_ceps": top_ceps
        }