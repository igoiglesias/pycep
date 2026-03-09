import os 
from dotenv import load_dotenv


load_dotenv()


VIACEP_URL = os.getenv("VIACEP_URL")
BRASILAPI_URL = os.getenv("BRASILAPI_URL")

DB_PATH = os.getenv("DB_PATH", "")

CACHE_ENABLE = os.getenv("CACHE_ENABLE") == "True"
CACHE_EXPIRE = int(os.getenv("CACHE_EXPIRE", "3600"))
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "")

DAYS_TO_UPDATE = int(os.getenv("DAYS_TO_UPDATE", "30"))
TENTATIVAS_TO_UPDATE = int(os.getenv("TENTATIVAS_TO_UPDATE", "3"))

USER_COOKIE_NAME = os.getenv("USER_COOKIE_NAME", "")
ADMIN_COOKIE_NAME = os.getenv("ADMIN_COOKIE_NAME", "")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
COOKIE_HTTPONLY = os.getenv("COOKIE_HTTPONLY") == "True"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE")
COOKIE_SECURE = os.getenv("COOKIE_SECURE") == "True"
COOKIE_MAX_AGE = int(os.getenv("COOKIE_MAX_AGE", "60"))

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "3600"))
