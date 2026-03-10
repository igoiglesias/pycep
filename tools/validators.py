from typing import Annotated, Literal
from fastapi import Path
from pydantic import BaseModel


CEP = Annotated[str, Path(description="Cep a ser consultado", min_length=8, max_length=9)]
PERFIL = Literal["user", "admin"]

class CEP_CONTENT(BaseModel):
    """
    Modelo de conteúdo para a consulta de CEP
    """
    cep: str
    logradouro: str
    complemento: str
    bairro: str
    localidade: str
    uf: str
    ibge: str
    gia: str
    ddd: str
    siafi: str

class CEP_RESPONSE(BaseModel):
    """
    Modelo de resposta para a consulta de CEP
    """
    erro: bool
    mensagem: str | None
    content: CEP_CONTENT | None
    