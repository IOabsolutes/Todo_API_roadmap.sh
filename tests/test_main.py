import pytest


@pytest.mark.asyncio
async def test_root(test_client):
    async for client in test_client:
        response = await client.get('/')
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
