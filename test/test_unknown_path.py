from unittest.mock import patch, AsyncMock
from web_api.main import app
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient


client = TestClient(app)
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_path():
    response = client.get("/jbfsdjbsjdbfjds")

    assert response.status_code == 200
