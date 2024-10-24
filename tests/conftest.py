import pytest
import pytest_asyncio

# P.S do not forget to point to the .env into configuration of the testsing!!!!!
from app.main import app
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlmodel import SQLModel
from app.db.session import engine
from app.models.user_model import User
from app.utils.token import generate_token
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

client = AsyncClient(app=app)

url = "http://fastapi.localhost"


@pytest_asyncio.fixture(scope='session', autouse=True)
async def init_db():
    logging.debug(SQLModel.metadata.tables, exc_info=True, stack_info=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        logging.info("Dropping all tables")
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest_asyncio.fixture(scope='function')
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# create test clinet
@pytest_asyncio.fixture(scope='function')
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=url, headers={"Content-Type": "application/json"}) as client:
        yield client


# Create test user into db
@pytest_asyncio.fixture(scope='function')
async def test_user(get_session) -> User:
    from app import crud
    from app.schemas.user_schema import IUserCreate
    user_data = IUserCreate(
        name="test",
        email="test@test.com",
        password="Test123@#",
    )
    user = await crud.user.create_user(obj_in=user_data, db_session=get_session)
    assert user is not None
    assert isinstance(user, User)
    return user


@pytest_asyncio.fixture(scope='function')
async def create_test_tasks(get_session, test_user) -> None:
    from app import crud
    from app.schemas.task_schema import ITaskCreate
    new_tasks_list = []
    task_data = [
        ITaskCreate(
            title=f"test{i}",
            description=f"test description {i}"
        ) for i in range(1, 10)]
    for task in task_data:
        new_task = await crud.task.create_task(new_task=task, user=test_user, db_session=get_session)
        new_tasks_list.append(new_task)
    assert new_tasks_list is not None
    assert len(new_tasks_list) == len(task_data)


@pytest_asyncio.fixture(scope='function')
def authorized_client(test_client: AsyncClient, test_user: User) -> AsyncClient:
    token_data = generate_token(test_user)
    test_client.cookies.set("access_token", token_data.access_token)
    test_client.cookies.set("refresh_token", token_data.refresh_token)
    test_client.headers["Authorization"] = f"Bearer {token_data.access_token}"
    return test_client
