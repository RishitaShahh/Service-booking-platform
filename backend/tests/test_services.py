"""Unit and API tests for Service management flows."""

import pytest
from httpx import AsyncClient


async def get_authenticated_headers(client: AsyncClient, email: str, role: str) -> dict:
    """Helper function to register, login, and return authorization headers."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": f"Test {role.title()}",
            "role": role
        }
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_provider_creates_service(client: AsyncClient):
    """Test service provider creating a service."""
    headers = await get_authenticated_headers(client, "prov1@example.com", "provider")

    service_payload = {
        "name": "Full House Cleaning",
        "description": "Deep cleaning service for residential houses.",
        "duration_minutes": 120,
        "price": 150.0,
        "is_active": True
    }
    res = await client.post("/api/v1/services", json=service_payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Full House Cleaning"
    assert data["price"] == 150.0


@pytest.mark.asyncio
async def test_customer_cannot_create_service(client: AsyncClient):
    """Test customer role is forbidden from creating services."""
    headers = await get_authenticated_headers(client, "cust1@example.com", "customer")

    service_payload = {
        "name": "Invalid Service",
        "description": "Customer trying to create service",
        "duration_minutes": 60,
        "price": 50.0
    }
    res = await client.post("/api/v1/services", json=service_payload, headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_services_public(client: AsyncClient):
    """Test public listing of active services."""
    headers = await get_authenticated_headers(client, "prov2@example.com", "provider")
    await client.post(
        "/api/v1/services",
        json={"name": "Plumbing Repair", "description": "Fix leaks", "duration_minutes": 60, "price": 80.0},
        headers=headers
    )

    res = await client.get("/api/v1/services")
    assert res.status_code == 200
    services = res.json()
    assert len(services) >= 1
    assert any(s["name"] == "Plumbing Repair" for s in services)
