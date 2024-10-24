from fastapi import APIRouter, Depends, Body, HTTPException, Response, status, Request
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from app.schemas.user_schema import IUserCreate
from app.deps import user_deps
from app import crud
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from app.utils.token import generate_token
from app.core.security import decode_token, create_access_token
from app.core.config import settings
from datetime import timedelta
from app.schemas.token_schema import TokenRead
from app.core.limiter import limiter

router = APIRouter()


class EmailPasswordRequestForm(OAuth2PasswordRequestForm):
    email: EmailStr
    password: str

    @classmethod
    def as_form(cls, email: str = "email", password: str = "password"):
        return cls(grant_type="password", email=email, password=password, scope="")


@router.post('/register')
@limiter.limit("100/minute", error_message="Too many requests")
async def register(request: Request, new_user: IUserCreate = Depends(user_deps.is_user_exist)) -> dict[str, str]:
    user = await crud.user.create_user(obj_in=new_user)
    token_data = generate_token(user)
    return {'Token': token_data.access_token}


@router.post('/login')
async def login(email: EmailStr = Body(...), password: str = Body(...), response: Response = Response()) -> dict[
    str, str]:
    user = await crud.user.authenticate(email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Email or Password incorrect")
    token_data = generate_token(user)
    response.set_cookie(key="access_token", value=token_data.access_token, httponly=True, secure=True)
    response.set_cookie(key="refresh_token", value=token_data.refresh_token, httponly=True, secure=True)
    return {'Token': token_data.access_token}


@router.post('/logout')
async def logout(response: Response = Response()) -> dict[str, str]:
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {'message': 'Logged out successfully'}


@router.get('/refresh')
async def refresh_access_token(refresh_token: str = Depends(user_deps.get_refresh_token),
                               response: Response = Response()) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your token has expired. Please log in again.",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error when decoding the token. Please check your request.",
        )
    except MissingRequiredClaimError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is no required field in your token. Please contact the administrator.",
        )

    if payload['type'] == "refresh":
        user_id = int(payload['sub'])
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        user = await crud.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_access_token = create_access_token(user.id, expires_delta=access_token_expires)
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True)
        return {'Token': new_access_token}
    else:
        raise HTTPException(status_code=401, detail="Invalid token type")


@router.post('/access-token')
async def get_access_token(response: Response,
                           form_data: OAuth2PasswordRequestForm = Depends()) -> TokenRead:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token_data = generate_token(user)
    response.set_cookie(key="access_token", value=token_data.access_token, httponly=True, secure=True)
    response.set_cookie(key="refresh_token", value=token_data.refresh_token, httponly=True, secure=True)
    return TokenRead(access_token=token_data.access_token, token_type="bearer")
