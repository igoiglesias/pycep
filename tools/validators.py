from typing import Annotated
from fastapi import Path


CEP = Annotated[str, Path(description="Cep a ser consultado", min_length=8, max_length=9)]