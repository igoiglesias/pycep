

class Admin:
    def __init__(self, repo):
        self.repo = repo

    async def get_dashboard(self) -> dict:
        total_consultas = await self.repo.get_total_consultas()
        total_erros = await self.repo.get_total_erros()
        avg_response_time = await self.repo.get_avg_response_time()
        total_users = await self.repo.get_total_users()
        top_ceps = await self.repo.get_top_ceps(5)
        consultas_por_mes = await self.repo.get_consultas_por_mes(6)
        consultas_por_dia = await self.repo.get_consultas_por_dia(30)
        erros_por_tipo = await self.repo.get_erros_por_tipo()

        taxa_erro = round((total_erros / total_consultas) * 100, 1) if total_consultas else 0

        return {
            "total_consultas": total_consultas,
            "total_erros": total_erros,
            "taxa_erro": taxa_erro,
            "avg_response_time": avg_response_time,
            "total_users": total_users,
            "top_ceps": [{"cep": r["cep"], "total": r["total"]} for r in (top_ceps or [])],
            "consultas_por_mes": [{"mes": r["mes"], "total": r["total"]} for r in (consultas_por_mes or [])],
            "consultas_por_dia": [{"dia": r["dia"], "total": r["total"]} for r in (consultas_por_dia or [])],
            "erros_por_tipo": [{"tipo": r["error_message"], "total": r["total"]} for r in (erros_por_tipo or [])],
        }
