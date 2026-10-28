"""Unit and integration tests for authentication."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_flow(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "engineer@example.com",
        "password": "Password123!",
        "full_name": "Arjun Sharma",
    }
    res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    user_data = res.json()
    assert user_data["email"] == "engineer@example.com"
    assert user_data["full_name"] == "Arjun Sharma"

    # 2. Duplicate registration should return 409
    res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_dup.status_code == 409

    # 3. Login
    login_payload = {
        "email": "engineer@example.com",
        "password": "Password123!",
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    token = token_data["access_token"]

    # 4. Get Current User Profile (/me)
    headers = {"Authorization": f"Bearer {token}"}
    res_me = await client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "engineer@example.com"


@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword!"},
    )
    assert res.status_code == 401
