from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.schemas.token_schema import Token
from app.models.user_model import User


def generate_token(user: User) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id, expires_delta=refresh_token_expires)
    data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    )
    return data
