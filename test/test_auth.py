from unittest.mock import patch, AsyncMock
from web_api.main import app
import pytest
from httpx import AsyncClient
from faker import Faker
from fastapi import HTTPException, status
from web_api.schemas.user import CreateUserRequest
from web_api.services.user import bcrypt_context, register_user
from web_api.routers.auth import create_user

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
async def test_register_user_exist():

    response = client.post("/register/", data={"username": "test_user", "password": "qwerty"})
    assert response.status_code == 401
    assert response.json() == {"error": "User with the same login already exists!"}


# @pytest.mark.asyncio
# async def test_user_create():
#     async with AsyncClient(base_url=BASE_URL) as client: # надо для работы с asyncpg
#         response = await client.post("/register", data={"username": "hgfhfgh", "password": "qwerty"})
#         assert response.status_code == 401  # Или другой ожидаемый статус


@pytest.mark.asyncio
async def test_user_login_page():
    response = client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_login_success():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/login", data={"username": "admin", "password": "passwd"})
        assert response.status_code == 302
        print(response.text)
        access_token = response.cookies.get("access_token")
        print(access_token)
        assert access_token is not None


# @pytest.mark.asyncio
# async def test_user_logout():
#     async with AsyncClient(base_url=BASE_URL) as client:
#         responce = await client.post("/login", data={"username": "admin", "password": "passwd"}, follow_redirects=True)
#         assert responce.status_code == 200
        

#         response = await client.get("/logout")
#         assert response.status_code == 303
#         assert "access_token" not in response.cookies
