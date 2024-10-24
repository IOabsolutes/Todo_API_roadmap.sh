from datetime import timedelta

import pytest

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user_schema import IUserCreate

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_register(test_client, get_session, init_db):
    test_data = IUserCreate(email='test@example.com', name='Lira', password='Test12@password')
    response = await test_client.post('/auth/register', json=test_data.dict())
    assert response.status_code == 200
    assert 'Token' in response.json()


@pytest.mark.asyncio
async def test_login(test_client, test_user, get_session, init_db):
    login_data = {'email': test_user.email, 'password': "Test123@#"}
    response = await test_client.post('/auth/login', json=login_data)

    assert response.status_code == 200
    assert 'Token' in response.json()

    access_token = test_client.cookies.get("access_token")
    refresh_token = test_client.cookies.get("refresh_token")
    assert access_token is not None
    assert refresh_token is not None


@pytest.mark.asyncio
async def test_logout(test_client, test_user):
    login_data = {'email': test_user.email, 'password': "Test123@#"}

    response = await test_client.post('/auth/login', json=login_data)
    assert response.status_code == 200

    response = await test_client.post('/auth/logout')
    assert response.status_code == 200
    assert response.json() == {'message': 'Logged out successfully'}

    access_token = test_client.cookies.get("access_token")
    refresh_token = test_client.cookies.get("refresh_token")
    assert access_token is None
    assert refresh_token is None


@pytest.mark.asyncio
async def test_refresh_access_token(authorized_client, init_db):
    response = await authorized_client.get('/auth/refresh')
    assert response.status_code == 200
    assert 'Token' in response.json()
