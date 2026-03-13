from collections.abc import Iterable, Callable
import aiosqlite
from datetime import datetime, timedelta, timezone
from config.config import DAYS_TO_UPDATE, TENTATIVAS_TO_UPDATE


class Repository:
    def __init__(self, get_db: Callable):
        self.db = get_db()


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
                existe INTEGER DEFAULT 1,
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
        
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS token (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user INTEGER NOT NULL,
                name TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user) REFERENCES user(id) ON DELETE CASCADE
            )
        ''')
        await self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_token ON token(token);")
        
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
        
        await self.db.execute("""CREATE TABLE IF NOT EXISTS fila_update (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'pending',
            request_log TEXT,
            tentativas INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        
        await self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_fila_update_cep ON fila_update(cep);")
        await self.db.execute("DROP TRIGGER IF EXISTS fila_updated_at_trigger;")
        await self.db.execute('''
            CREATE TRIGGER fila_updated_at_trigger
            AFTER UPDATE ON fila_update
            FOR EACH ROW
            BEGIN
                UPDATE fila_update
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
        ''')


    async def incrementar_uso(self, cep: str):
        query = 'UPDATE cep SET usage_count = usage_count + 1 WHERE cep = ?'
        return await self.db.execute(query, (cep,))


    async def has_to_update(self, cep: str) -> aiosqlite.Row | None:
        limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_UPDATE)
        query = 'SELECT id FROM cep WHERE cep = ? AND updated_at < ?'
        return await self.db.fetchone(query, (cep, limit_date,))


    async def get_cep(self, cep: str) -> aiosqlite.Row | None:
        query = 'SELECT cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi, existe FROM cep WHERE cep = ?'
        return await self.db.fetchone(query, (cep,))

    async def save_cep(self, cep_data: dict, cep: str) -> None:
        query  = '''
            INSERT INTO cep (cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi, existe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        await self.db.execute(query, (
            cep,
            cep_data['content'].get('logradouro'),
            cep_data['content'].get('complemento'),
            cep_data['content'].get('unidade'),
            cep_data['content'].get('bairro'),
            cep_data['content'].get('localidade'),
            cep_data['content'].get('uf'),
            cep_data['content'].get('estado'),
            cep_data['content'].get('regiao'),
            cep_data['content'].get('ibge'),
            cep_data['content'].get('gia'),
            cep_data['content'].get('ddd'),
            cep_data['content'].get('siafi'),
            0 if cep_data['erro'] else 1
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
        query = 'SELECT SUM(usage_count) as total FROM cep'
        return await self.db.fetchone(query)
    

    async def get_top_ceps(self) -> Iterable[aiosqlite.Row] | None:
        query = 'SELECT cep, usage_count FROM cep ORDER BY usage_count DESC LIMIT 5'
        return await self.db.fetchall(query)


    async def get_admin(self, email: str) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM admin WHERE email = ? and active = 1'
        return await self.db.fetchone(query, (email,))


    async def get_user(self, email: str) -> aiosqlite.Row | None:
        query = 'SELECT id, email, password FROM user WHERE email = ? and active = 1'
        return await self.db.fetchone(query, (email,))


    async def get_admin_by_id(self, admin_id: int) -> aiosqlite.Row | None:
        query = 'SELECT id, email, name FROM admin WHERE id = ? and active = 1'
        return await self.db.fetchone(query, (admin_id,))


    async def get_user_by_id(self, user_id: int) -> aiosqlite.Row | None:
        query = 'SELECT id, email, name FROM user WHERE id = ? and active = 1'
        return await self.db.fetchone(query, (user_id,))


    async def get_user_by_email(self, email: str) -> aiosqlite.Row | None:
        query = 'SELECT id FROM user WHERE email = ?'
        return await self.db.fetchone(query, (email,))


    async def create_user(self, name: str, email: str, password_hash: str) -> None:
        query = '''
            INSERT INTO user (name, email, password)
            VALUES (?, ?, ?)
        '''
        await self.db.execute(query, (name, email, password_hash))



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
    
    
    async def add_to_fila_update(self, cep: str) -> None:
        query = '''
            INSERT INTO fila_update (cep)
            VALUES (?);
        '''
        await self.db.execute(query, (cep,))
    

    async def get_fila_update(self) -> Iterable[aiosqlite.Row] | None:
        query = '''
            SELECT id, cep, tentativas FROM fila_update
            WHERE status = 'pending' and tentativas <= ?
            ORDER BY created_at ASCexecute
            LIMIT 10;
        '''
        return await self.db.fetchall(query, (TENTATIVAS_TO_UPDATE,))
    
    
    async def remove_from_fila_update(self, cep: str) -> None:
        query = '''
            DELETE FROM fila_update
            WHERE cep = ?;
        '''
        await self.db.execute(query, (cep,))


    async def increment_update_attempts(self, cep: str) -> None:
        query = '''
            UPDATE fila_update
            SET tentativas = tentativas + 1
            WHERE cep = ?;
        '''
        await self.db.execute(query, (cep,))
    

    async def set_error_fila_update(self, cep: str) -> None:
        query = '''
            UPDATE fila_update
            SET status = 'error'
            WHERE cep = ?;
        '''
        await self.db.execute(query, (cep,))


    async def get_tokens_by_user_id(self, user_id: int) -> Iterable[aiosqlite.Row] | None:
        query = '''
            SELECT id, name, token FROM token
            WHERE user = ? and active = 1 
            ORDER BY created_at DESC
        '''
        return await self.db.fetchall(query, (user_id,))


    async def create_token(self, user_id: int, name: str, token: str) -> None:
        query = '''
            INSERT INTO token (user, name, token)
            VALUES (?, ?, ?)
        '''
        await self.db.execute(query, (user_id, name, token))
    
    
    async def delete_token(self, user_id: int, token_id: int) -> None:
        query = '''
            DELETE FROM token
            WHERE id = ? and user = ?;
        '''
        await self.db.execute(query, (token_id, user_id,))
