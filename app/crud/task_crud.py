from typing import Sequence
from fastapi import HTTPException
from .base_crud import CRUDBase
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from app.models.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common_schema import IOrderEnum
from sqlmodel import select
from sqlalchemy import exc
from app.schemas.task_schema import ITaskCreate, ITaskUpdate, ITaskRead, IOrderByTaskEnum
from datetime import date
from ..models import Task


class CRUDTasks(CRUDBase[Task, ITaskCreate, ITaskUpdate, ITaskRead]):

    async def get_multy_tasks_paginated(
            self,
            *,
            params: Params | None = Params(),
            current_user: User,
            db_session: AsyncSession | None = None
    ) -> Page[Task]:
        db_session = db_session or self.db.session
        query = select(Task).where(Task.user_id == current_user.id)
        output = await paginate(db_session, query, params)
        return output

    async def get_multy_tasks_filtered_by_date(
            self,
            *,
            params: Params | None = Params(),
            current_user: User,
            from_date: date,
            to_date: date,
            db_session: AsyncSession | None = None
    ) -> Page[Task]:
        db_session = db_session or self.db.session
        query = select(Task).where(Task.user_id == current_user.id).where(Task.create_at.between(from_date, to_date))
        output = await paginate(db_session, query, params)
        return output

    async def get_multy_tasks_sorted(
            self,
            *,
            params: Params | None = Params(),
            order_by: IOrderByTaskEnum | None = IOrderByTaskEnum.id,
            order: IOrderEnum | None = IOrderEnum.ascendant,
            current_user: User,
            db_session: AsyncSession | None = None
    ) -> Page[Task]:
        db_session = db_session or self.db.session

        columns = Task.__table__.columns

        if order == IOrderEnum.ascendant:
            query = select(Task).where(Task.user_id == current_user.id).order_by(columns[order_by].asc())
        else:
            query = select(Task).where(Task.user_id == current_user.id).order_by(columns[order_by].desc())
        output = await paginate(db_session, query, params)
        return output

    async def get_task_by_owner_id(
            self,
            id: int,
            current_user: User,
            db_session: AsyncSession | None = None
    ) -> Task:
        task = await self.get_task_by_id(id, db_session)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to access this task")
        return task

    async def get_users_tasks_by_id(self, user_id: int, db_session: AsyncSession | None = None) -> Sequence[Task]:
        db_session = db_session or self.db.session
        query = select(Task).where(Task.user_id == user_id)
        result = await db_session.execute(query)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int, db_session: AsyncSession | None = None) -> Task | None:
        db_session = db_session or self.db.session
        query = select(Task).where(Task.id == task_id)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    async def create_task(
            self,
            new_task: ITaskCreate,
            user: User,
            db_session: AsyncSession | None = None
    ) -> Task:
        db_session = db_session or self.db.session
        task_data = new_task.dict()
        task_data['user_id'] = user.id
        task = Task(**task_data)
        try:
            db_session.add(task)
            await db_session.commit()
        except exc.IntegrityError:
            db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(task)
        return task

    async def update_task(self, task_id: int, new_data: Task, current_user: User, db_session: AsyncSession | None = None
                          ) -> Task:
        db_session = db_session or self.db.session
        task = await self.get_task_by_owner_id(id=task_id, current_user=current_user)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )
        for key, value in new_data.dict(exclude_unset=True).items():
            setattr(task, key, value)
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)
        return task

    async def remove_task(self, task_id: int, current_user: User, db_session: AsyncSession | None = None) -> Task:
        db_session = db_session or self.db.session
        task = await self.get_task_by_owner_id(id=task_id, current_user=current_user)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )
        await db_session.delete(task)
        await db_session.commit()
        return task


task = CRUDTasks(Task)
