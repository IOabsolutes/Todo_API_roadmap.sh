from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.core.security import decode_token
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from app.models.user_model import User
from app import crud

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/access-token"
)


async def get_current_user(token: str = Depends(reusable_oauth2)) -> User:
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expired"
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    except MissingRequiredClaimError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is no required field in your token. Please contact the administrator"
        )
    user_id = int(payload.get("sub"))

    user: User = await crud.user.get_by_id(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
