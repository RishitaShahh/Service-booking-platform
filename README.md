# Service Booking Platform (Python FastAPI + React Vite)

A complete, production-quality, decoupled **Service Booking Platform** with a Python FastAPI backend (SQLAlchemy 2.0 Async, Pydantic v2, Alembic migrations, Pytest, JWT Auth) and a React SPA frontend (Vite, Tailwind CSS, Lucide React).

---

## Key Features

- **Decoupled Architecture:** Backend JSON API (with OpenAPI/Swagger docs at `/docs`) and React SPA frontend.
- **Role-Based Access Control:** Separate workflows for `customer` and `provider` accounts with JWT token security.
- **Race-Condition & Double-Booking Prevention:** DB-level row locking (`FOR UPDATE`) and atomic state transitions to guarantee time slots cannot be double-booked under concurrent requests.
- **Automatic Slot Release:** Cancelling a booking automatically releases the time slot back to `available` status.
- **Provider Isolation:** Service providers can only view and manage their own services, slots, and incoming bookings.
- **Automated Testing:** Pytest suite with `httpx.AsyncClient` covering authentication, service management, slot generation, booking, double-booking prevention, and slot release flows.

---

## Tech Stack

### Backend
- Python 3.11+
- **FastAPI** (Async ASGI Web Framework)
- **SQLAlchemy 2.0** (Async ORM)
- **PostgreSQL** (Production DB) / **SQLite (aiosqlite)** (Local Dev / Pytest fallback)
- **Alembic** (Database Migrations)
- **Pydantic v2** (Request / Response validation schemas)
- **Pytest** + **HTTPX AsyncClient** (Testing suite)

### Frontend
- **React 18** (Vite)
- **Tailwind CSS** (Utility-first styling)
- **Lucide React** (Icons)
- **Axios** (REST API Client)

---

## Getting Started

### 1. Prerequisites
- Python 3.11+ installed
- Node.js (v18+) and npm installed
- PostgreSQL installed (optional; SQLite fallback is configured by default for zero-dependency quickstart)

---

### 2. Backend Setup & Run

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. Run database migrations with Alembic:
   ```bash
   alembic upgrade head
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - OpenAPI/Swagger Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc Interactive Docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

7. Run backend test suite:
   ```bash
   pytest -v
   ```

---

### 3. Frontend Setup & Run

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Open browser at: [http://localhost:5173](http://localhost:5173)

---

## Technical Documentation

For the complete end-to-end technical documentation including system architecture diagrams, database schemas, full OpenAPI endpoint reference with request/response payloads, service method reference, business rules implementation, and frontend API mappings, see **[`PROJECT_DOCUMENTATION.md`](./PROJECT_DOCUMENTATION.md)**.
