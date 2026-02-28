import sqlite3
from config.config import DB_PATH, DAYS_TO_UPDATE
from datetime import datetime, timedelta, timezone


def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn.cursor()


def initialize_db(db_path=DB_PATH):
    cursor = get_db_connection(db_path)
    cursor.execute('''
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
            usage_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cep ON cep(cep);")
    cursor.execute("DROP TRIGGER IF EXISTS cep_updated_at_trigger;")
    cursor.execute('''
        CREATE TRIGGER cep_updated_at_trigger
        AFTER UPDATE ON cep
        FOR EACH ROW
        BEGIN
            UPDATE cep
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
    ''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE, 
        password TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_admin ON admin(email);")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS request_log (
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
    
    cursor.connection.commit()
    cursor.connection.close()


def incrementar_uso(cep):
    cursor = get_db_connection()
    cursor.execute('UPDATE cep SET usage_count = usage_count + 1 WHERE cep = ?', (cep,))
    cursor.connection.commit()
    cursor.connection.close()


def has_to_update(cep):
    limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_UPDATE)
    cursor = get_db_connection()
    cursor.execute('SELECT cep FROM cep WHERE cep = ? and updated_at < ?', (cep, limit_date,))
    return cursor.fetchone()


def get_cep(cep):
    cursor = get_db_connection()
    cursor.execute('SELECT cep, logradouro, complemento, unidade, bairro, localidade, uf, estado, regiao, ibge, gia, ddd, siafi FROM cep WHERE cep = ?', (cep,))
    return cursor.fetchone()


def save_cep(cep_data):
    cursor = get_db_connection()
    cursor.execute('''
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
    cursor.connection.commit()
    cursor.connection.close()


def update_cep(cep_data):
    cursor = get_db_connection()
    cursor.execute('''
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
    cursor.connection.commit()
    cursor.connection.close()

def get_total_consultas():
    cursor = get_db_connection()
    cursor.execute('SELECT sum(usage_count) as total FROM cep')
    return cursor.fetchone()

def get_top_ceps():
    cursor = get_db_connection()
    cursor.execute('SELECT cep, usage_count FROM cep ORDER BY usage_count DESC LIMIT 5')
    return cursor.fetchall()


def get_admin(email):
    cursor = get_db_connection()
    cursor.execute('SELECT id, email, password FROM admin WHERE email = ? and active = 1', (email,))
    return cursor.fetchone()


def get_admin_by_id(admin_id):
    cursor = get_db_connection()
    cursor.execute('SELECT id, email, name FROM admin WHERE id = ? and active = 1', (admin_id,))
    return cursor.fetchone()


def save_request_log(cep, ip, user_agent, user_token, user_id, error, error_message, response_time):
    cursor = get_db_connection()
    cursor.execute('''
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
    cursor.connection.commit()
    cursor.connection.close()