# Service Booking Platform — Project Documentation

## Table of Contents
1. Project Overview
2. Problem Statement
3. Features
4. User Roles
5. Functional Requirements
6. Business Rules
7. Database Entities and Relationships
8. Project Architecture
9. API Endpoints
10. Booking Flow
11. Time Slot Flow
12. Installation and Running Steps
13. Demo Credentials
14. Testing
15. Out-of-Scope Features
16. Future Scope

---

## 1. Project Overview

The **Service Booking Platform** is a web application that connects customers with service providers. Customers browse services, view time slots, and make bookings. Providers create services, manage availability, and view/manage bookings.

- **Frontend:** React (Vite) + Tailwind CSS — http://localhost:5173
- **Backend:** Python FastAPI (async) — http://localhost:8000
- **Database:** SQLite (file: backend/service_booking.db)
- **Auth:** JWT tokens with two roles: customer and provider

---

## 2. Problem Statement

Build a service booking platform where:
- Customers browse services, view available time slots, book appointments, and manage bookings.
- Service Providers create/manage services, define availability, and manage customer bookings.
- The system prevents double-bookings — no two customers can book the same time slot.

---

## 3. Features

### Customer Features
- Register and log in as a customer
- Browse all available services
- View service details (name, description, duration, price, provider)
- View available time slots for a service
- Book an appointment for a selected slot
- View booking history (all, confirmed, cancelled)
- Cancel a booking (slot is released back to available)

### Provider Features
- Register and log in as a provider
- Create and manage services (name, description, duration, price in INR)
- Define available time slots (individual or batch creation)
- View all bookings for their services
- Cancel bookings
- Provider dashboard with booking statistics

---

## 4. User Roles

| Role | Description |
|------|-------------|
| Customer | End user who browses and books services |
| Provider | Professional who offers services and manages availability |

Role is selected at registration and enforced by the backend on every protected endpoint.

---

## 5. Functional Requirements

### Authentication
- Users register with name, email, password, and role
- Users log in and receive a JWT access token
- Protected endpoints require: Authorization: Bearer token

### Services
- Providers create, update, and delete their own services
- Anyone can list services (no login required)
- Service info: name, description, duration (minutes), price (INR), provider

### Time Slots
- Providers define slots with date, start time, end time
- Slots created individually or in batch (date range + interval)
- Slot status: available or booked
- Customers see only available slots for a chosen service

### Bookings
- Customers book an available slot for a service
- Booking links: customer, service, provider, time slot
- Booking status: confirmed or cancelled
- Customers cancel their own confirmed bookings
- Cancellation releases the slot (status returns to available)
- Providers view and cancel bookings for their own services

---

## 6. Business Rules

| Rule | How Enforced |
|------|--------------|
| A slot cannot be double-booked | Row lock (SELECT FOR UPDATE) + slot.status == available check |
| Customers cannot book unavailable slots | Backend rejects if slot.status != available |
| Cancellation releases the slot | cancel_booking() sets booking and slot status atomically in one DB transaction |
| Providers manage only their own data | Backend checks service.provider_id == current_user.id |
| Customers cancel only their own bookings | Backend checks booking.customer_id == current_user.id |
| Simultaneous booking attempts handled safely | Row lock + IntegrityError catch returns HTTP 409 Conflict |

---

## 7. Database Entities and Relationships

### users
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| name | String | Full name |
| email | String UNIQUE | Login email |
| hashed_password | String | bcrypt hash |
| role | Enum | customer or provider |
| created_at | DateTime | Registration timestamp |

### services
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| provider_id | FK users.id | Owner |
| name | String | Service name |
| description | Text | Details |
| duration_minutes | Integer | Length of service |
| price | Float | Price in INR |
| is_active | Boolean | Soft-delete flag |
| created_at | DateTime | Creation timestamp |

### time_slots
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| provider_id | FK users.id | Owner |
| service_id | FK services.id | Optional assignment |
| slot_date | Date | Calendar date |
| start_time | Time | Start time |
| end_time | Time | End time |
| status | Enum | available or booked |
| created_at | DateTime | Creation timestamp |

### bookings
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| customer_id | FK users.id | The customer |
| service_id | FK services.id | The service |
| provider_id | FK users.id | The provider |
| slot_id | FK time_slots.id | The time slot |
| status | Enum | confirmed or cancelled |
| created_at | DateTime | Booking timestamp |

### Relationships
- One provider -> many services
- One service -> many time slots
- One time slot -> many bookings (but only one confirmed at a time)
- One customer -> many bookings

---

## 8. Project Architecture

```
Service Booking Platform/
beta backend/
    app/
        main.py             # App entry point, routers, DB init
        database.py         # Async SQLAlchemy engine and session
        core/
            config.py       # Settings from .env
            security.py     # JWT and password utilities
        models/             # ORM models (user, service, slot, booking)
        schemas/            # Pydantic v2 request/response schemas
        services/           # Business logic layer
        routers/            # FastAPI route handlers
    alembic/                # DB migration files
    tests/                  # Pytest test suite (10 tests)
    .env                    # Environment config
    requirements.txt        # Python dependencies
    service_booking.db      # SQLite database (auto-created)

frontend/
    src/
        api/client.js           # Axios with auth token interceptor
        context/AuthContext.jsx # JWT state, login/logout, role helpers
        components/             # Navbar, ServiceCard, SlotPicker, etc.
        pages/                  # One component per screen/route
        utils/dateUtils.js      # formatDate, formatTime, formatCurrency (INR)
    .env                    # VITE_API_BASE_URL
    package.json
```

**Architecture Pattern:**
- Decoupled: backend is pure REST JSON API; frontend is React SPA
- Layered backend: Routes -> Service (business logic) -> Models (DB)
- Fully async: FastAPI + SQLAlchemy 2.0 + aiosqlite

---

## 9. API Endpoints

All routes prefixed with /api/v1. Interactive docs at http://localhost:8000/docs

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | None | Register user |
| POST | /auth/login | None | Login, get JWT |
| GET | /auth/me | Bearer | Current user profile |

### Services
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /services | None | List all services |
| GET | /services/{id} | None | Service details |
| POST | /services | Provider | Create service |
| PUT | /services/{id} | Provider | Update service |
| DELETE | /services/{id} | Provider | Delete service |

### Time Slots
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /slots | Customer | Available slots (filter by service_id) |
| POST | /slots | Provider | Create one slot |
| POST | /slots/batch | Provider | Create many slots |
| GET | /slots/provider | Provider | Provider's own slots |
| DELETE | /slots/{id} | Provider | Delete a slot |

### Bookings
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /bookings | Customer | Create booking |
| GET | /bookings/my-bookings | Customer | My bookings |
| POST | /bookings/{id}/cancel | Customer | Cancel booking |

### Provider
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /providers/dashboard | Provider | Stats dashboard |
| GET | /providers/bookings | Provider | All provider bookings |
| POST | /providers/bookings/{id}/cancel | Provider | Cancel a booking |

---

## 10. Booking Flow

1. Customer browses services (GET /services)
2. Customer views service details (GET /services/{id})
3. Customer views available slots (GET /slots?service_id=X)
4. Customer selects a slot and clicks Book
5. Frontend sends POST /bookings with slot_id and service_id
6. Backend acquires a row lock on the slot (SELECT FOR UPDATE)
7. Backend checks slot.status == available
8. Backend creates booking (status=confirmed) and sets slot.status = booked
9. Both changes committed in one atomic transaction
10. Customer sees booking confirmed

Cancellation flow:
1. Customer clicks Cancel on a booking
2. Frontend sends POST /bookings/{id}/cancel
3. Backend sets booking.status = cancelled AND slot.status = available in one transaction
4. Slot is now bookable by others

---

## 11. Time Slot Flow

1. Provider logs in
2. Provider creates a service (POST /services)
3. Provider creates time slots (POST /slots or POST /slots/batch)
4. Slots appear as available to customers
5. When a customer books a slot, its status changes to booked
6. If booking is cancelled, slot returns to available
7. Provider views all slots from Manage Slots page

---

## 12. Installation and Running Steps

### Requirements
- Python 3.11 or newer
- Node.js 18 or newer
- No external database installation needed (SQLite is built in)

---

### Step 1: Backend Setup

```
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows):
venv\Scripts\activate

# Install packages:
pip install -r requirements.txt
```

Create backend/.env with:
```
DATABASE_URL=sqlite+aiosqlite:///./service_booking.db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Start the backend:
```
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL: http://127.0.0.1:8000
Swagger API Docs: http://127.0.0.1:8000/docs

The SQLite database is created automatically on first startup.

---

### Step 2: Frontend Setup

Open a NEW terminal window:

```
cd frontend
npm install
```

Create frontend/.env if not present:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Start the frontend:
```
npm run dev
```

Frontend URL: http://localhost:5173

---

### Quick Reference

| Terminal | Folder | Command | URL |
|----------|--------|---------|-----|
| 1 (Backend) | backend/ | python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload | http://127.0.0.1:8000 |
| 2 (Frontend) | frontend/ | npm run dev | http://localhost:5173 |

Open http://localhost:5173 in your browser.

---

## 13. Demo Credentials

The database starts empty. You must register accounts first.

### Register a Provider
- URL: http://localhost:5173/register
- Name: Demo Provider
- Email: provider@demo.com
- Password: password123
- Role: Provider

### Register a Customer
- URL: http://localhost:5173/register
- Name: Demo Customer
- Email: customer@demo.com
- Password: password123
- Role: Customer

### Demo Walkthrough
1. Login as provider -> Create a service -> Create time slots
2. Login as customer -> Browse services -> Book a slot -> Cancel if needed

---

## 14. Testing

Run all tests:
```
cd backend
python -m pytest -v
```

All 10 tests pass.

| Test | What It Checks |
|------|----------------|
| test_register_customer | Registration works correctly |
| test_register_duplicate_email_fails | Duplicate email rejected with 400 |
| test_login_and_access_me_endpoint | Login + JWT + /auth/me endpoint |
| test_provider_creates_service | Provider can create a service |
| test_customer_cannot_create_service | Customer gets 403 on service creation |
| test_list_services_public | Anyone can list services without login |
| test_successful_booking | Customer books an available slot |
| test_double_booking_prevented | Same slot cannot be booked twice |
| test_simultaneous_booking_conflict_prevention | Two concurrent requests: only one wins |
| test_cancel_booking_releases_slot | Cancellation sets slot back to available |

The simultaneous booking test uses asyncio.gather() to fire two requests at the same time. Row-level locking ensures exactly one succeeds.

---

## 15. Out-of-Scope Features

The following are intentionally NOT implemented:
- Payment gateway
- Video consultation
- SMS or WhatsApp integration
- Complex recurring appointments
- Multi-location enterprise scheduling

---

## 16. Future Scope

- Email notifications for booking confirmation and cancellation
- Calendar view for provider availability
- Customer ratings and reviews for services
- Service search and category filters
- Admin panel for platform management
- Mobile application
