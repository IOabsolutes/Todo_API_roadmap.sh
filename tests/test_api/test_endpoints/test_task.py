import pytest
from app.schemas.task_schema import ITaskCreate, ITaskUpdate
from app import crud


@pytest.mark.asyncio
async def test_get_tasks(authorized_client, init_db, create_test_tasks):
    response = await authorized_client.get("/task")
    assert response.status_code == 200
    assert response.json() is not None


@pytest.mark.asyncio
async def test_create_task(authorized_client, init_db, get_session):
    new_task_data = ITaskCreate(title="test", description="test description")
    response = await authorized_client.post("/task", json=new_task_data.dict())
    assert response.status_code == 201

    renew_task = await crud.task.get_by_id(1, db_session=get_session)
    assert new_task_data.title == renew_task.title
    assert new_task_data.description == renew_task.description


@pytest.mark.asyncio
async def test_update_task(authorized_client, init_db, get_session, create_test_tasks):
    renew_task_data = ITaskUpdate(title="New_test_title", description="New_test_description")
    response = await authorized_client.put(f"/task?id={1}", json=renew_task_data.dict())
    assert response.status_code == 200

    renew_task = await crud.task.get_by_id(1, db_session=get_session)
    assert renew_task_data.title == renew_task.title
    assert renew_task_data.description == renew_task.description


@pytest.mark.asyncio
async def test_delete_task(authorized_client, init_db, get_session, create_test_tasks):
    response = await authorized_client.delete(f"/task?id={1}")
    assert response.status_code == 204

    deleted_task = await crud.task.get_by_id(1, db_session=get_session)
    assert deleted_task is None
