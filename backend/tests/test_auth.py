"""Unit and API tests for Authentication registration and login flows."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_customer(client: AsyncClient):
    """Test registering a customer user account."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "customer@example.com",
            "password": "password123",
            "full_name": "Jane Customer",
            "phone": "555-0199",
            "role": "customer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "customer@example.com"
    assert data["role"] == "customer"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient):
    """Test registering duplicate email fails with 400 Bad Request."""
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "User One",
        "role": "customer"
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_and_access_me_endpoint(client: AsyncClient):
    """Test logging in and fetching current user profile using JWT token."""
    # 1. Register user
    reg_payload = {
        "email": "provider@example.com",
        "password": "securepassword",
        "full_name": "Dr. Provider",
        "role": "provider"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login
    login_payload = {
        "email": "provider@example.com",
        "password": "securepassword"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Access /me endpoint with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "provider@example.com"
    assert me_data["role"] == "provider"
