from datetime import date
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi_pagination import Params, Page

from app.api.deps import get_current_user
from app.models.user_model import User
from app.schemas.task_schema import ITaskCreate, ITaskUpdate
from app.models.task_model import Task
from app.schemas.common_schema import IOrderEnum
from app.schemas.task_schema import IOrderByTaskEnum
from app.core.limiter import limiter
from app import crud

router = APIRouter()


@router.get("")
async def get_task(params: Params = Depends(), user: User = Depends(get_current_user)) -> Page[Task]:
    tasks = await crud.task.get_multy_tasks_paginated(params=params, current_user=user)
    return tasks


@router.get('/sorted')
async def get_sorted_task(
        params: Params = Depends(),
        order_by: IOrderByTaskEnum = Query(default=IOrderByTaskEnum.id, description="It's optional. Default is id"),
        order: IOrderEnum = Query(default=IOrderEnum.ascendant, description="It's optional. Default is ascendant"),
        user: User = Depends(get_current_user)
) -> Page[Task]:
    tasks = await crud.task.get_multy_tasks_sorted(
        params=params,
        order_by=order_by,
        order=order,
        current_user=user
    )
    return tasks


@router.get('/filtered')
async def get_filtered_by_date_tasks(
        params: Params = Depends(),
        from_date: date = Query(default=date.today(), description="It's optional. Default is now"),
        to_date: date = Query(default=date.today(), description="It's optional. Default is now"),
        user: User = Depends(get_current_user)
) -> Page[Task]:
    tasks = await crud.task.get_multy_tasks_filtered_by_date(
        params=params,
        from_date=from_date,
        to_date=to_date,
        current_user=user
    )
    return tasks


@router.post("", status_code=201)
@limiter.limit("100/minute", error_message="Too many requests")
async def create_task(new_task: ITaskCreate, request: Request, current_user: User = Depends(get_current_user)) -> Task:
    task = await crud.task.create_task(new_task, current_user)
    return task


@router.put("")
@limiter.limit("100/minute", error_message="Too many requests")
async def update_task(
        id: int,
        new_data: ITaskUpdate,
        request: Request,
        current_user: User = Depends(get_current_user)) -> Task:
    taks = await crud.task.update_task(id, new_data, current_user=current_user)
    return taks


@router.delete("", status_code=204)
async def remove_task(id: int, current_user: User = Depends(get_current_user)):
    await crud.task.remove_task(id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
