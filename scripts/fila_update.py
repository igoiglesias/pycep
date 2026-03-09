import asyncio
from databases.db import DB
from config import config
from services.cep import CEP
from modules.viacep import ViaCEP
from modules.brasilapi import BrasilAPI
from databases.repository import Repository




async def main():
    db = DB(config.DB_PATH)

    await db.connect()
    def get_db():
        return db

    repo = Repository(get_db)
    viacep = ViaCEP()
    brasilapi = BrasilAPI()
    cep_service = CEP(repo, viacep, brasilapi)
    
    await cep_service.processar_fila_update()
    
    await db.disconnect()




if __name__ == "__main__":
    asyncio.run(main())