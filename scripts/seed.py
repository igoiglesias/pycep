import asyncio
from tools.password import Password
from databases.db import DB
from config import config




async def main():
    db = DB(config.DB_PATH)
    await db.connect()
    
    await create_users(db)
    await create_request_logs(db)
    
    await db.disconnect()
    

    

async def create_users(db):
    password = Password()

    admin_pwd = password.hash('admin')
    admin_query = "INSERT OR IGNORE INTO admin (name, email, password) VALUES ('Admin', 'admin@pycep.com', ?)"
    await db.execute(admin_query, (admin_pwd,))
    
    user_pwd = password.hash('user')
    user_query = "INSERT OR IGNORE INTO user (name, email, password) VALUES ('User', 'user@pycep.com', ?)"
    await db.execute(user_query, (user_pwd,))


async def create_request_logs(db):
    request_data = [
        # --- MÊS 1: NOVEMBRO 2025 ---
        ('01310-100', '189.34.102.5', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_001', 101, 0, None, 0.125, '2025-11-01 09:15:22'),
        ('20040-002', '201.55.12.99', 'Mozilla/5.0 (Macintosh)', None, None, 0, None, 0.230, '2025-11-02 14:10:05'),
        ('99999-999', '177.10.11.12', 'PostmanRuntime/7.26.8', None, None, 1, 'CEP not found', 0.055, '2025-11-03 11:00:00'),
        ('30130-010', '189.1.2.3', 'Mozilla/5.0 (iPhone)', 'tok_nov_004', 205, 0, None, 0.198, '2025-11-05 16:45:12'),
        ('04578-000', '200.200.200.1', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_005', 101, 0, None, 0.110, '2025-11-07 08:30:45'),
        ('70050-000', '191.20.30.40', 'Mozilla/5.0 (Linux)', None, None, 0, None, 0.350, '2025-11-08 19:20:10'),
        ('12345-000', '168.0.0.1', 'curl/7.68.0', None, None, 1, 'Invalid format', 0.020, '2025-11-10 03:15:00'),
        ('80020-220', '179.12.34.56', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_008', 303, 0, None, 0.145, '2025-11-12 10:05:30'),
        ('22222-222', '10.0.0.55', 'Go-http-client/1.1', 'tok_api_999', 999, 1, 'Rate limit exceeded', 0.010, '2025-11-15 15:00:00'),
        ('60025-060', '201.88.99.77', 'Mozilla/5.0 (Macintosh)', None, None, 0, None, 0.215, '2025-11-18 09:00:15'),
        ('40020-010', '187.50.60.70', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_012', 404, 0, None, 0.175, '2025-11-20 13:40:22'),
        ('00000-000', '192.168.1.100', 'python-requests/2.25.1', None, None, 1, 'Invalid format', 0.040, '2025-11-22 17:10:05'),
        ('90010-100', '177.99.88.77', 'Mozilla/5.0 (iPad)', None, None, 0, None, 0.250, '2025-11-24 20:30:00'),
        ('50050-000', '189.44.55.66', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_015', 505, 0, None, 0.160, '2025-11-25 10:15:30'),
        ('70000-000', '200.10.20.30', 'Mozilla/5.0 (X11)', None, None, 1, 'Service unavailable', 5.000, '2025-11-27 12:00:00'),
        ('11111-111', '192.168.0.50', 'PostmanRuntime/7.26.8', None, None, 1, 'CEP not found', 0.060, '2025-11-30 22:10:10'),

        # --- MÊS 2: DEZEMBRO 2025 ---
        ('01311-000', '177.20.30.40', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_dec_001', 601, 0, None, 0.150, '2025-12-01 10:00:00'),
        ('20021-000', '189.50.60.70', 'Mozilla/5.0 (Android 11)', None, None, 0, None, 0.300, '2025-12-03 15:20:10'),
        ('88888-888', '192.168.1.5', 'curl/7.74.0', None, None, 1, 'CEP not found', 0.045, '2025-12-05 09:05:00'),
        ('04578-000', '200.200.200.1', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_005', 101, 0, None, 0.115, '2025-12-06 11:30:25'),
        ('30130-999', '189.1.2.3', 'Mozilla/5.0 (iPhone)', 'tok_nov_004', 205, 1, 'CEP not found', 0.080, '2025-12-08 14:15:40'),
        ('50000-000', '191.10.10.10', 'Mozilla/5.0 (Linux)', None, None, 0, None, 0.280, '2025-12-10 18:45:00'),
        ('12345-678', '168.10.20.30', 'PostmanRuntime/7.28.0', None, None, 1, 'Invalid format', 0.030, '2025-12-12 08:10:15'),
        ('80020-220', '179.12.34.56', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_008', 303, 0, None, 0.155, '2025-12-14 12:25:30'),
        ('99999-000', '10.0.0.60', 'Go-http-client/1.1', 'tok_api_999', 999, 1, 'Server Error', 1.500, '2025-12-17 20:00:00'),
        ('60025-060', '201.88.99.77', 'Mozilla/5.0 (Macintosh)', None, None, 0, None, 0.225, '2025-12-19 09:30:20'),
        ('40020-010', '187.50.60.70', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_012', 404, 0, None, 0.185, '2025-12-21 13:55:45'),
        ('11111-000', '192.168.1.101', 'python-requests/2.26.0', None, None, 1, 'Invalid format', 0.050, '2025-12-23 10:40:10'),
        ('70000-111', '200.10.20.30', 'Mozilla/5.0 (X11)', None, None, 1, 'CEP not found', 0.070, '2025-12-27 14:30:50'),
        ('30130-010', '189.1.2.3', 'Mozilla/5.0 (iPhone)', 'tok_nov_004', 205, 0, None, 0.190, '2025-12-28 17:45:20'),
        ('22222-333', '192.168.0.51', 'PostmanRuntime/7.28.0', None, None, 1, 'Rate limit exceeded', 0.020, '2025-12-30 23:25:30'),
        ('01310-100', '189.34.102.5', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_001', 101, 0, None, 0.140, '2025-12-31 18:50:00'),

        # --- MÊS 3: JANEIRO 2026 ---
        ('01415-000', '177.30.40.50', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_jan_001', 701, 0, None, 0.160, '2026-01-02 08:30:15'),
        ('20550-000', '189.60.70.80', 'Mozilla/5.0 (Android 12)', None, None, 0, None, 0.320, '2026-01-04 12:45:00'),
        ('77777-777', '192.168.1.10', 'curl/7.80.0', None, None, 1, 'CEP not found', 0.055, '2026-01-06 16:10:30'),
        ('04578-000', '200.200.200.1', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_005', 101, 0, None, 0.120, '2026-01-08 09:25:45'),
        ('30130-010', '189.1.2.3', 'Mozilla/5.0 (iPhone)', 'tok_nov_004', 205, 0, None, 0.200, '2026-01-10 14:50:10'),
        ('69000-000', '191.50.50.50', 'Mozilla/5.0 (Linux)', None, None, 0, None, 0.380, '2026-01-12 19:15:25'),
        ('ABCDE-123', '168.20.30.40', 'PostmanRuntime/7.29.0', None, None, 1, 'Invalid format', 0.035, '2026-01-14 11:30:05'),
        ('80020-220', '179.12.34.56', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_008', 303, 0, None, 0.165, '2026-01-16 15:40:50'),
        ('88888-000', '10.0.0.70', 'Go-http-client/1.1', 'tok_api_999', 999, 1, 'Timeout', 2.000, '2026-01-20 22:20:00'),
        ('60025-060', '201.88.99.77', 'Mozilla/5.0 (Macintosh)', None, None, 0, None, 0.235, '2026-01-22 08:45:15'),
        ('00000-111', '192.168.1.102', 'python-requests/2.27.0', None, None, 1, 'Invalid format', 0.060, '2026-01-26 17:35:05'),
        ('70000-000', '200.10.20.30', 'Mozilla/5.0 (X11)', None, None, 0, None, 0.360, '2026-01-29 16:30:20'),
        ('33333-333', '192.168.0.52', 'PostmanRuntime/7.29.0', None, None, 1, 'Rate limit exceeded', 0.025, '2026-01-31 18:35:35'),
        ('01310-100', '189.34.102.5', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_001', 101, 0, None, 0.150, '2026-01-31 23:59:00'),

        # --- MÊS 4: FEVEREIRO 2026 ---
        ('01500-000', '177.40.50.60', 'Mozilla/5.0 (Windows NT 11.0)', 'tok_feb_001', 801, 0, None, 0.170, '2026-02-01 10:20:15'),
        ('21000-000', '189.70.80.90', 'Mozilla/5.0 (Android 13)', None, None, 0, None, 0.340, '2026-02-02 14:45:30'),
        ('66666-666', '192.168.1.15', 'curl/7.82.0', None, None, 1, 'CEP not found', 0.065, '2026-02-04 09:10:00'),
        ('04578-000', '200.200.200.1', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_005', 101, 0, None, 0.125, '2026-02-05 13:35:25'),
        ('69000-111', '191.50.50.50', 'Mozilla/5.0 (Linux)', None, None, 1, 'CEP not found', 0.090, '2026-02-09 08:15:15'),
        ('XYZ-987', '168.30.40.50', 'PostmanRuntime/7.30.0', None, None, 1, 'Invalid format', 0.040, '2026-02-11 12:40:40'),
        ('77777-000', '10.0.0.80', 'Go-http-client/1.1', 'tok_api_999', 999, 1, 'Server Error', 1.800, '2026-02-17 11:55:55'),
        ('40020-010', '187.50.60.70', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_012', 404, 0, None, 0.205, '2026-02-21 09:45:45'),
        ('00000-222', '192.168.1.103', 'python-requests/2.28.0', None, None, 1, 'Invalid format', 0.070, '2026-02-23 14:10:10'),
        ('50050-000', '189.44.55.66', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_015', 505, 0, None, 0.190, '2026-02-25 22:50:00'),
        ('70000-000', '200.10.20.30', 'Mozilla/5.0 (X11)', None, None, 0, None, 0.370, '2026-02-26 08:15:25'),
        ('30130-010', '189.1.2.3', 'Mozilla/5.0 (iPhone)', 'tok_nov_004', 205, 0, None, 0.215, '2026-02-27 12:40:50'),
        ('44444-444', '192.168.0.53', 'PostmanRuntime/7.30.0', None, None, 1, 'Rate limit exceeded', 0.030, '2026-02-28 21:30:40'),
        ('01310-100', '189.34.102.5', 'Mozilla/5.0 (Windows NT 10.0)', 'tok_nov_001', 101, 0, None, 0.160, '2026-02-28 23:45:00'),
    ]

    sql = """
        INSERT INTO request_log 
        (cep, ip, user_agent, user_token, user_id, error, error_message, response_time, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for request in request_data:
        await db.execute(sql, request)



if __name__ == "__main__":
    asyncio.run(main())