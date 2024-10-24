from .base_crud import CRUDBase
from app.models.user_model import User
from app.schemas.user_schema import IUserCreate, IUserUpdate, IUserRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate, IUserRead]):

    async def get_by_email(self, *, email: str, db_session: AsyncSession | None = None) -> User | None:
        db_session = db_session or super().get_db().session
        user = await db_session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    async def authenticate(self, *, email: str, password: str, db_session: AsyncSession | None = None) -> User | None:
        db_session = db_session or super().get_db().session
        user = await self.get_by_email(email=email, db_session=db_session)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def create_user(self, *, obj_in: IUserCreate, db_session: AsyncSession | None = None) -> User:
        db_session = db_session or super().get_db().session
        password_hash = get_password_hash(obj_in.password)
        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            password_hash=password_hash,
        )
        db_session.add(
            db_obj
        )
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
