# Tech Stack Documentation
## Service Booking Platform

This document explains every technology and library used in this project, and WHY it was chosen.

---

## Backend Technologies

### 1. Python
**What:** The programming language used for the entire backend.
**Why:** Python is beginner-friendly, widely used in web development, and has a massive ecosystem of libraries. It is the natural choice for building REST APIs quickly.

---

### 2. FastAPI
**What:** A modern Python web framework for building REST APIs.
**Why:** FastAPI is async-first (handles many requests at once), automatically generates interactive API documentation (Swagger at /docs), and uses Python type hints for validation. It is significantly faster than Flask and Django for I/O-heavy tasks.

**Key features used:**
- Async route handlers
- Dependency injection (for auth, DB session)
- Automatic request body validation
- Automatic Swagger UI at /docs
- CORS middleware

---

### 3. SQLAlchemy 2.0 (Async ORM)
**What:** The database ORM (Object-Relational Mapper) used to interact with the database.
**Why:** Instead of writing raw SQL queries, SQLAlchemy lets us define database tables as Python classes (models). SQLAlchemy 2.0 supports async operations natively, which is required for FastAPI's async architecture.

**Key features used:**
- Async engine and sessions (AsyncEngine, AsyncSession)
- ORM model definitions (User, Service, TimeSlot, Booking)
- SELECT ... FOR UPDATE (row-level locking to prevent double bookings)
- Relationship definitions

---

### 4. aiosqlite
**What:** An async SQLite driver for Python.
**Why:** SQLite is a file-based database that requires zero installation or configuration. aiosqlite lets SQLAlchemy talk to SQLite in async mode. Perfect for local development and demos.

---

### 5. SQLite (Database)
**What:** A lightweight, file-based relational database.
**Why chosen for this project:** No server to install, no configuration, works everywhere. The database is stored in a single file: service_booking.db. For production, this would be replaced with PostgreSQL.

---

### 6. Alembic
**What:** A database migration tool for SQLAlchemy.
**Why:** When you change a database model (add a column, rename a table), you need a way to update the database schema without losing data. Alembic manages these changes as versioned migration scripts.

---

### 7. Pydantic v2
**What:** A data validation library used for request and response schemas.
**Why:** FastAPI uses Pydantic to validate incoming request data and format outgoing response data. Pydantic v2 is faster and stricter than v1. It catches invalid data (wrong types, missing fields) before it ever reaches the business logic.

**Key features used:**
- BaseModel for request/response schemas
- EmailStr for email validation
- Field with constraints (min_length, ge for prices)

---

### 8. python-jose
**What:** A Python library for creating and verifying JSON Web Tokens (JWT).
**Why:** JWT is the standard way to handle stateless authentication in REST APIs. After login, the server creates a signed token. The client sends it with every request. The server verifies the signature — no database lookup needed for auth.

---

### 9. passlib with bcrypt
**What:** A password hashing library.
**Why:** Passwords must never be stored in plain text. passlib with bcrypt hashes passwords using a slow, secure algorithm that is designed to be hard to crack even if the database is compromised.

**Important note:** bcrypt is pinned to version 4.0.1 in requirements.txt because bcrypt 5.x is incompatible with passlib.

---

### 10. Uvicorn
**What:** An ASGI server that runs the FastAPI application.
**Why:** FastAPI is an ASGI framework, which requires an ASGI server. Uvicorn is the standard choice — it is fast, production-ready, and supports async.

**Used with --reload flag during development** so the server restarts automatically when code changes.

---

### 11. Pytest
**What:** The testing framework used for all backend tests.
**Why:** Pytest is the most popular Python testing framework. It has a simple, readable syntax and integrates well with async code via pytest-asyncio.

---

### 12. pytest-asyncio
**What:** A Pytest plugin that allows testing async functions.
**Why:** Since FastAPI and SQLAlchemy are async, tests must also run async code. pytest-asyncio enables this with the @pytest.mark.asyncio decorator.

---

### 13. httpx
**What:** An async HTTP client library used in tests.
**Why:** FastAPI's recommended way to test endpoints is via httpx.AsyncClient. It can make HTTP requests directly to the FastAPI app without a running server, making tests fast and self-contained.

---

### 14. pydantic-settings
**What:** A Pydantic extension for loading configuration from environment variables.
**Why:** App configuration (database URL, JWT secret, CORS origins) should not be hardcoded. pydantic-settings reads values from a .env file and validates them as typed Python settings.

---

### 15. python-multipart
**What:** A library for parsing form data.
**Why:** FastAPI's OAuth2PasswordRequestForm (used for the login endpoint) requires form data parsing, which needs python-multipart installed.

---

## Frontend Technologies

### 16. React 18
**What:** A JavaScript library for building user interfaces.
**Why:** React lets us build a dynamic, interactive single-page application (SPA). Each UI element is a component that automatically re-renders when its data changes. React 18 adds concurrent rendering improvements.

---

### 17. Vite
**What:** A modern frontend build tool and development server.
**Why:** Vite is much faster than older tools like Create React App. It uses native ES modules during development (no bundling needed), so the dev server starts instantly and hot-reloads changes in milliseconds.

---

### 18. Tailwind CSS
**What:** A utility-first CSS framework.
**Why:** Instead of writing custom CSS, Tailwind provides hundreds of small utility classes (like flex, p-4, text-blue-500) that can be composed to build any design. This makes styling fast and consistent without fighting with CSS specificity.

---

### 19. PostCSS
**What:** A tool that processes CSS using plugins.
**Why:** Tailwind CSS requires PostCSS to transform its utility classes into real CSS. Without postcss.config.js configured properly, Tailwind would not compile. This was added as a fix during development.

---

### 20. Axios
**What:** A JavaScript HTTP client library.
**Why:** Axios makes it easy to call the backend REST API from the frontend. It supports request/response interceptors — used here to automatically attach the JWT token to every API request from the Authorization header.

---

### 21. React Router DOM v6
**What:** A routing library for React.
**Why:** React is a single-page application — there is only one HTML page. React Router DOM handles navigation between different views (services list, service detail, bookings, etc.) by updating the URL and rendering the right component.

**Key features used:**
- BrowserRouter, Routes, Route
- useNavigate (programmatic navigation)
- useParams (reading URL parameters like service ID)
- Protected routes (redirect if not logged in or wrong role)

---

### 22. Lucide React
**What:** A library of SVG icons as React components.
**Why:** Icons make the UI more intuitive and professional. Lucide React provides clean, consistent icons (calendar, clock, user, etc.) as ready-to-use React components that can be styled with Tailwind.

---

### 23. React Context API
**What:** A built-in React feature for sharing state across components.
**Why:** Authentication state (who is logged in, their role, their JWT token) needs to be accessible from any component in the app. React Context (AuthContext) avoids passing these values as props through every component layer.

---

## Summary Table

| Category | Technology | Purpose |
|----------|-----------|----------|
| Language | Python | Backend programming language |
| API Framework | FastAPI | Build REST API endpoints |
| ORM | SQLAlchemy 2.0 | Interact with database as Python objects |
| DB Driver | aiosqlite | Async SQLite driver |
| Database | SQLite | File-based relational database |
| Migrations | Alembic | Manage database schema changes |
| Validation | Pydantic v2 | Validate request/response data |
| Auth Tokens | python-jose | Create and verify JWT tokens |
| Passwords | passlib + bcrypt | Hash and verify passwords securely |
| Server | Uvicorn | ASGI server to run FastAPI |
| Testing | Pytest + pytest-asyncio | Run automated backend tests |
| HTTP Testing | httpx | Make async HTTP requests in tests |
| Config | pydantic-settings | Load config from .env file |
| UI Framework | React 18 | Build interactive frontend |
| Build Tool | Vite | Fast dev server and bundler |
| Styling | Tailwind CSS | Utility-first CSS styling |
| CSS Processing | PostCSS | Process Tailwind CSS |
| HTTP Client | Axios | Make API calls from frontend |
| Routing | React Router DOM v6 | Client-side navigation |
| Icons | Lucide React | SVG icon components |
| State | React Context API | Share auth state across components |
