import jwt as PyJWT
from datetime import datetime, timedelta, timezone
from config import config


def create_token(user_id: int) -> str:
        """Cria um token JWT para o admin."""
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
        }
        return PyJWT.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)