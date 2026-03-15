

class Admin:
    def __init__(self, repo):
        self.repo = repo
    
    async def get_dashboard(self) -> dict:
        """
        Retorna os dados do dashboard.
        """
        total_consultas = ""
        top_ceps = []
        return {
            "total_consultas": total_consultas,
            "top_ceps": top_ceps
        }