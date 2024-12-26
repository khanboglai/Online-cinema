from unittest.mock import patch, AsyncMock
from web_api.main import app
import pytest
from httpx import AsyncClient, Cookies
from fastapi.testclient import TestClient


client = TestClient(app)
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_register():
    
    # Выполняем запрос на регистрацию
    response = client.get("/register/")

    # Проверяем статус код и ответ
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_create():
    async with AsyncClient(base_url=BASE_URL) as client: # надо для работы с asyncpg
        response = await client.post("/register", data={"username": "hgfhfgh", "password": "qwerty"})
        assert response.status_code == 401  # Или другой ожидаемый статус


@pytest.mark.asyncio
async def test_user_login_page():
    response = client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_login_success():
    async with AsyncClient(base_url=BASE_URL) as client:
        # client.cookies = Cookies
        response = await client.post("/login", data={"username": "admin", "password": "passwd"}, follow_redirects=True)
        assert response.status_code == 200
        print(response.headers)
        access_token = response.cookies.get("access_token")
        # print(access_token)
        assert access_token is None
