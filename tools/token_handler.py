import jwt as PyJWT
from datetime import datetime, timedelta, timezone
from config import config


def create_token(user_id: int) -> str:
    """Cria um token JWT para o admin."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    }
    return PyJWT.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica um token JWT."""
    try:
        return PyJWT.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except PyJWT.ExpiredSignatureError:
        return {}