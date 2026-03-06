import aiosqlite
from config.config import DB_PATH, DAYS_TO_UPDATE
from datetime import datetime, timedelta, timezone


async def get_db_connection(db_path=DB_PATH):
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    return conn


async def initialize_db(db_path=DB_PATH):
    cursor = await get_db_connection(db_path)
    await cursor.execute('''
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
    await cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cep ON cep(cep);")
    await cursor.execute("DROP TRIGGER IF EXISTS cep_updated_at_trigger;")
    await cursor.execute('''
        CREATE TRIGGER cep_updated_at_trigger
        AFTER UPDATE ON cep
        FOR EACH ROW
        BEGIN
            UPDATE cep
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
    ''')
    
    await cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE, 
        password TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    await cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_admin ON admin(email);")
    
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, 
            password TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    await cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user ON user(email);")
    
    await cursor.execute("""CREATE TABLE IF NOT EXISTS request_log (
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
    
    await cursor.commit()
    await cursor.close()


async def incrementar_uso(cep):
    db = await get_db_connection()
    cursor = await db.execute('UPDATE cep SET usage_count = usage_count + 1 WHERE cep = ?', (cep,))
    await cursor.close()
    await db.commit()
    await db.close()


async def has_to_update(cep):
    limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_UPDATE)
    db = await get_db_connection()
    cursor = await db.execute('SELECT cep FROM cep WHERE cep = ? and updated_at < ?', (cep, limit_date,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def get_cep(cep):
    db = await get_db_connection()
    cursor = await db.execute('SELECT cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi FROM cep WHERE cep = ?', (cep,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def save_cep(cep_data):
    db = await get_db_connection()
    await db.execute('''
        INSERT INTO cep (cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
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
    db.commit()
    db.close()


async def update_cep(cep_data):
    db = await get_db_connection()
    await db.execute('''
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
    ''', (
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
    db.commit()
    db.close()

async def get_total_consultas():
    db = await get_db_connection()
    cursor = await db.execute('SELECT sum(usage_count) as total FROM cep')
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row

async def get_top_ceps():
    db = await get_db_connection()
    cursor = await db.execute('SELECT cep, usage_count FROM cep ORDER BY usage_count DESC LIMIT 5')
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows
    


async def get_admin(email):
    db = await get_db_connection()
    cursor = await db.execute('SELECT id, email, password FROM admin WHERE email = ? and active = 1', (email,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def get_user(email):
    db = await get_db_connection()
    cursor = await db.execute('SELECT id, email, password FROM user WHERE email = ? and active = 1', (email,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def get_admin_by_id(admin_id):
    db = await get_db_connection()
    cursor = await db.execute('SELECT id, email, name FROM admin WHERE id = ? and active = 1', (admin_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def get_user_by_id(user_id):
    db = await get_db_connection()
    cursor = await db.execute('SELECT id, email, name FROM user WHERE id = ? and active = 1', (user_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row


async def save_request_log(cep, ip, user_agent, user_token, user_id, error, error_message, response_time):
    cursor = await get_db_connection()
    await cursor.execute('''
        INSERT INTO request_log (cep, ip, user_agent, user_token, user_id, error, error_message, response_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        cep,
        ip,
        user_agent,
        user_token,
        user_id,
        error,
        error_message,
        response_time
    ))
    await cursor.commit()
    await cursor.close()