"""Unit and API tests for core Booking business logic, cancellation, and simultaneous conflict prevention flows."""

import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


async def setup_provider_service_and_slot(client: AsyncClient, email: str = "prov_book@example.com"):
    """Helper fixture setup creating provider, service, and available slot."""
    # 1. Register & login provider
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Dr. Smith", "role": "provider"}
    )
    p_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    p_token = p_login.json()["access_token"]
    p_headers = {"Authorization": f"Bearer {p_token}"}

    # 2. Create service
    s_res = await client.post(
        "/api/v1/services",
        json={"name": "Medical Consultation", "description": "General health check", "duration_minutes": 30, "price": 100.0},
        headers=p_headers
    )
    service_id = s_res.json()["id"]

    # 3. Create single time slot in future (10:00 AM - 10:30 AM)
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0).isoformat()
    end_time = (now + timedelta(days=1)).replace(hour=10, minute=30, second=0).isoformat()

    slot_res = await client.post(
        "/api/v1/slots",
        json={"service_id": service_id, "start_time": start_time, "end_time": end_time, "status": "available"},
        headers=p_headers
    )
    slot_id = slot_res.json()["id"]

    return service_id, slot_id, p_headers


async def get_customer_headers(client: AsyncClient, email: str = "cust_book@example.com"):
    """Helper to register and login a customer user."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Alice Cooper", "role": "customer"}
    )
    c_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    c_token = c_login.json()["access_token"]
    return {"Authorization": f"Bearer {c_token}"}


@pytest.mark.asyncio
async def test_successful_booking(client: AsyncClient):
    """Test customer successfully booking an available slot."""
    service_id, slot_id, _ = await setup_provider_service_and_slot(client, "prov101@example.com")
    c_headers = await get_customer_headers(client, "cust101@example.com")

    booking_payload = {"service_id": service_id, "slot_id": slot_id, "notes": "First appointment"}
    res = await client.post("/api/v1/bookings", json=booking_payload, headers=c_headers)
    assert res.status_code == 201
    b_data = res.json()
    assert b_data["status"] == "confirmed"
    assert b_data["slot_id"] == slot_id


@pytest.mark.asyncio
async def test_double_booking_prevented(client: AsyncClient):
    """Test Business Rule 1 & 2: Double booking of the same slot is rejected."""
    service_id, slot_id, _ = await setup_provider_service_and_slot(client, "prov102@example.com")
    c1_headers = await get_customer_headers(client, "cust102a@example.com")
    c2_headers = await get_customer_headers(client, "cust102b@example.com")

    booking_payload = {"service_id": service_id, "slot_id": slot_id}

    # Customer 1 books slot
    res1 = await client.post("/api/v1/bookings", json=booking_payload, headers=c1_headers)
    assert res1.status_code == 201

    # Customer 2 attempts to book the same slot
    res2 = await client.post("/api/v1/bookings", json=booking_payload, headers=c2_headers)
    assert res2.status_code in [400, 409]
    assert "no longer available" in res2.json()["detail"].lower() or "race condition" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_simultaneous_booking_conflict_prevention(client: AsyncClient):
    """Test simultaneous rapid booking attempts for the same 10:00 AM - 10:30 AM slot.

    Requirements Verified:
    - Only ONE booking is confirmed.
    - The other request is rejected with a meaningful message.
    - The slot cannot have two confirmed bookings.
    """
    service_id, slot_id, _ = await setup_provider_service_and_slot(client, "prov_conflict@example.com")
    c1_headers = await get_customer_headers(client, "cust_conflict_a@example.com")
    c2_headers = await get_customer_headers(client, "cust_conflict_b@example.com")

    booking_payload = {"service_id": service_id, "slot_id": slot_id}

    # Fire simultaneous concurrent booking requests
    res1, res2 = await asyncio.gather(
        client.post("/api/v1/bookings", json=booking_payload, headers=c1_headers),
        client.post("/api/v1/bookings", json=booking_payload, headers=c2_headers),
    )

    statuses = [res1.status_code, res2.status_code]
    
    # Exactly one request must be HTTP 201 Created
    assert statuses.count(201) == 1
    
    # Exactly one request must be rejected (400 Bad Request or 409 Conflict)
    rejected_res = res1 if res1.status_code != 201 else res2
    assert rejected_res.status_code in [400, 409]
    
    # Rejected request must return a clear, meaningful message
    error_detail = rejected_res.json()["detail"].lower()
    assert "no longer available" in error_detail or "race condition" in error_detail or "already been booked" in error_detail


@pytest.mark.asyncio
async def test_cancel_booking_releases_slot(client: AsyncClient):
    """Test Business Rule 3: Cancelling a booking releases slot back to available status."""
    service_id, slot_id, _ = await setup_provider_service_and_slot(client, "prov103@example.com")
    c_headers = await get_customer_headers(client, "cust103@example.com")

    # 1. Book slot
    b_res = await client.post(
        "/api/v1/bookings",
        json={"service_id": service_id, "slot_id": slot_id},
        headers=c_headers
    )
    booking_id = b_res.json()["id"]

    # 2. Cancel booking
    cancel_res = await client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=c_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # 3. Verify slot is now available again for booking
    slots_res = await client.get(f"/api/v1/slots?service_id={service_id}")
    available_slots = slots_res.json()
    assert any(s["id"] == slot_id and s["status"] == "available" for s in available_slots)

    # 4. Another customer can now book the released slot
    c2_headers = await get_customer_headers(client, "cust103b@example.com")
    rebook_res = await client.post(
        "/api/v1/bookings",
        json={"service_id": service_id, "slot_id": slot_id},
        headers=c2_headers
    )
    assert rebook_res.status_code == 201
