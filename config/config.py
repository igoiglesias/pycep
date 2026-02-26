from pickle import TRUE


VIACEP_URL = "https://viacep.com.br/ws"
BRASILAPI_URL = "https://brasilapi.com.br/api"

DB_PATH = "databases/database.db"

CACHE_ENABLE = True
CACHE_EXPIRE = 60
CACHE_PREFIX = "pycep"

DAYS_TO_UPDATE = 30

COOKIE_HTTPONLY = TRUE
COOKIE_SAMESITE = "lax"
COOKIE_SECURE = TRUE
COOKIE_MAX_AGE = 60

JWT_SECRET = "pycep"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 3600