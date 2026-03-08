from fastapi import APIRouter, Request, BackgroundTasks
from tools.validators import CEP, CEP_RESPONSE
from modules.viacep import ViaCEP
from modules.brasilapi import BrasilAPI
from services.cep import CEP as CEPService
from services.log import log as LogService
from bootstrap import get_db
from databases.repository import Repository


router = APIRouter(
    prefix="/cep",
    tags=["Api"]
)

repo = Repository(get_db)

viacep = ViaCEP()
brasilapi = BrasilAPI()
cep_service = CEPService(repo, viacep, brasilapi)
log_service = LogService(repo)


@router.get("/{cep}", response_model=CEP_RESPONSE)
@log_service.cep_request
async def consulta_cep(request: Request, cep: CEP, background_tasks: BackgroundTasks):
    """
    Consulta o CEP informado
    """
    return await cep_service.consultar(cep, background_tasks)