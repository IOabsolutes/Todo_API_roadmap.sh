from app import crud
from app.schemas.user_schema import IUserCreate
from fastapi import HTTPException, Request


async def is_user_exist(new_user: IUserCreate) -> IUserCreate:
    user = await crud.user.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists",
        )
    return new_user


async def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token not found")
    return token
