from collections.abc import Iterable
import aiosqlite
from datetime import datetime, timedelta, timezone
from config.config import DAYS_TO_UPDATE


class Repository:
    def __init__(self, db):
        self.db = db


    async def initialize_db(self) -> None:
        """Cria as tabelas, indices e triggers necessários no banco de dados, se ainda não existirem."""
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS cep (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cep TEXT NOT NULL UNIQUE,
                logradouro TEXT,
                complemento TEXT,
                unidade TEXT,
                bairro TEXT,
                localidade TEXT,
                uf TEXT,
                estado TEXT,
                regiao TEXT,
                ibge TEXT,
                gia TEXT,
                ddd TEXT,
                siafi TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cep ON cep(cep);")
        await self.db.execute("DROP TRIGGER IF EXISTS cep_updated_at_trigger;")
        await self.db.execute('''
            CREATE TRIGGER cep_updated_at_trigger
            AFTER UPDATE ON cep
            FOR EACH ROW
            BEGIN
                UPDATE cep
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
        ''')
        
        await self.db.execute('''CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, 
            password TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_admin ON admin(email);")
        
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, 
                password TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user ON user(email);")
        
        await self.db.execute("""CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep TEXT NOT NULL,
            ip TEXT NOT NULL,
            user_agent TEXT,
            user_token TEXT,
            user_id INTEGER,
            error INTEGER DEFAULT 0,
            error_message TEXT,
            response_time FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")


    async def incrementar_uso(self, cep: str):
        query = 'UPDATE cep SET usage_count = usage_count + 1 WHERE cep = ?'
        return await self.db.execute(query, (cep,))


    async def has_to_update(self, cep: str) -> aiosqlite.Row | None:
        limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_UPDATE)
        query = 'SELECT id FROM cep WHERE cep = ? AND updated_at < ?'
        return await self.db.fetchone(query, (cep, limit_date,))


    async def get_cep(self, cep: str) -> aiosqlite.Row | None:
        query = 'SELECT cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi FROM cep WHERE cep = ?'
        return await self.db.fetchone(query, (cep,))

    async def save_cep(self, cep_data: dict) -> None:
        query  = '''
            INSERT INTO cep (cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        await self.db.execute(query, (
            cep_data['cep'],
            cep_data['logradouro'],
            cep_data['complemento'],
            cep_data['unidade'],
            cep_data['bairro'],
            cep_data['localidade'],
            cep_data['uf'],
            cep_data['estado'],
            cep_data['regiao'],
            cep_data['ibge'],
            cep_data['gia'],
            cep_data['ddd'],
            cep_data['siafi']
        ))


    async def update_cep(self, cep_data: dict) -> None:
        query  = '''
            UPDATE cep SET
                logradouro = ?,
                complemento = ?,
                bairro = ?,
                unidade = ?,
                localidade = ?,
                uf = ?,
                estado = ?,
                regiao = ?,
                ibge = ?,
                gia = ?,
                ddd = ?,
                siafi = ?
            WHERE cep = ?
        '''
        await self.db.execute(query, (
            cep_data['logradouro'],
            cep_data['complemento'],
            cep_data['bairro'],
            cep_data['unidade'],
            cep_data['localidade'],
            cep_data['uf'],
            cep_data['estado'],
            cep_data['regiao'],
            cep_data['ibge'],
            cep_data['gia'],
            cep_data['ddd'],
            cep_data['siafi'],
            cep_data['cep']
        ))


    async def get_total_consultas(self) -> aiosqlite.Row | None:
        query = 'SELECT SUM(usage_count) as total_consultas FROM cep'
        return await self.db.execute(query)
    

    async def get_top_ceps(self) -> Iterable[aiosqlite.Row] | None:
        query = 'SELECT cep, usage_count FROM cep ORDER BY usage_count DESC LIMIT 5'
        return await self.db.execute(query)


    async def get_admin(self, email: str) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM admin WHERE email = ? and active = 1'
        return await self.db.fetchone(query, (email,))


    async def get_user(self, email: str) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM user WHERE email = ? and active = 1'
        return await self.db.fetchone(query, (email,))

    async def get_admin_by_id(self, admin_id: int) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM admin WHERE id = ? and active = 1'
        return await self.db.fetchone(query, (admin_id,))


    async def get_user_by_id(self, user_id: int) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM user WHERE id = ? and active = 1'
        return await self.db.fetchone(query, (user_id,))

    async def save_request_log(self, cep: str, ip: str, user_agent: str, user_token: str, user_id: int, error: bool, error_message: str, response_time: float) -> None:
        query = '''
            INSERT INTO request_log (cep, ip, user_agent, user_token, user_id, error, error_message, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        await self.db.execute(query, (
            cep,
            ip,
            user_agent,
            user_token,
            user_id,
            error,
            error_message,
            response_time
        ))