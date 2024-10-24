from typing import Generic, TypeVar
from sqlalchemy import exc
from fastapi import HTTPException
from sqlmodel import SQLModel
from fastapi_async_sqlalchemy import db
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType, SchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
        self.db = db

    def get_db(self) -> type(db):
        return self.db

    async def get_by_id(self, id: int, db_session: AsyncSession | None = None) -> ModelType | None:
        db_session = db_session or self.db.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def create(
            self,
            *,
            obj_in: CreateSchemaType | ModelType,
            db_session: AsyncSession | None = None) \
            -> ModelType:
        db_session = db_session or self.db.session
        db_obj = self.model.validate(obj_in)
        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj
