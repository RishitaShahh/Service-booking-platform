# Interview Q&A
## Service Booking Platform

This document contains simple, natural-sounding interview questions and answers based specifically on this project. Read through these and practice saying them in your own words.

---

## Section 1: Project Introduction

**Q: Tell me about the project you built.**

A: I built a Service Booking Platform — a web application where customers can browse services, view available time slots, and book appointments. Service providers can create their services, manage their time slots, and view or cancel bookings. It is basically a platform that connects customers with service providers for scheduling appointments.

---

**Q: Why did you build this project?**

A: The goal was to build a real-world booking system that handles the core challenges of any scheduling application — like preventing two customers from booking the same slot at the same time, managing different user roles, and keeping the booking and slot status in sync.

---

**Q: What can a customer do in this system?**

A: A customer can register, log in, browse all available services, view the details of a service including its price and duration, see the available time slots for a service, book a slot, view their booking history, and cancel a booking. When they cancel, the slot becomes available again for others to book.

---

**Q: What can a service provider do?**

A: A provider can register, log in, create and manage their services with details like name, description, price, and duration. They can also create time slots — either one at a time or in bulk. They can view all bookings made for their services and cancel them if needed. There is also a dashboard that shows summary statistics.

---

## Section 2: Tech Stack

**Q: What technologies did you use in this project?**

A: For the backend, I used Python with FastAPI as the web framework, SQLAlchemy for the database ORM, and SQLite as the database. For authentication, I used JWT tokens with the python-jose library, and bcrypt for password hashing. For the frontend, I used React with Vite as the build tool, Tailwind CSS for styling, and Axios to make API calls. I also used React Router for navigation between pages.

---

**Q: Why did you choose FastAPI for the backend?**

A: FastAPI is async-first, which means it can handle many requests simultaneously without blocking. It also automatically generates interactive API documentation (Swagger UI) at /docs, which makes testing and development much easier. It uses Python type hints, so data validation is built in.

---

**Q: Why did you use React for the frontend?**

A: React lets me build a dynamic, component-based UI where each part of the page only re-renders when its data changes. It is very popular and has a large ecosystem. I used Vite as the build tool because it is much faster than older alternatives — the dev server starts instantly.

---

**Q: Why did you choose SQLite instead of PostgreSQL?**

A: SQLite is file-based and requires zero installation, which makes it perfect for local development and demos. The project was built with SQLAlchemy ORM, so switching to PostgreSQL later would just require changing the database URL in the .env file — no code changes needed.

---

## Section 3: Database and API

**Q: What are the main tables in your database?**

A: There are four main tables: users, services, time_slots, and bookings. Users stores both customers and providers (differentiated by a role column). Services stores the service details created by providers. Time_slots stores the available slots created by providers. Bookings connects customers, services, providers, and time slots together and tracks the booking status.

---

**Q: How are the tables related to each other?**

A: A provider (user) can have many services. A service can have many time slots. A customer (user) can have many bookings. Each booking is linked to one customer, one service, one provider, and one time slot. So a booking ties everything together.

---

**Q: What kind of API did you build?**

A: I built a REST API with JSON responses. All endpoints are under /api/v1. There are endpoints for authentication, services, time slots, bookings, and provider-specific actions. The API has interactive documentation at /docs generated automatically by FastAPI.

---

**Q: How does your API handle different user roles?**

A: The backend has FastAPI dependencies called get_current_customer and get_current_provider. When a route uses these dependencies, FastAPI automatically checks the JWT token, extracts the role, and returns a 403 Forbidden error if the role does not match. So a customer trying to create a service gets rejected by the backend.

---

## Section 4: Authentication

**Q: How does authentication work in your project?**

A: When a user registers, their password is hashed using bcrypt and stored in the database. When they log in, the backend checks the password hash and if correct, creates a JWT access token. The frontend stores this token and sends it with every API request in the Authorization: Bearer header. The backend verifies the token signature on each request.

---

**Q: What is a JWT token?**

A: JWT stands for JSON Web Token. It is a signed string that contains information like the user's email, role, and user ID. The signature ensures the token cannot be tampered with. The server creates the token on login, and the client sends it back on every request. The server just verifies the signature — it does not need to look up the database to know who the user is.

---

**Q: Where is the JWT token stored on the frontend?**

A: It is stored in localStorage. The AuthContext in React manages reading and writing the token, and Axios automatically attaches it to every API request via an interceptor.

---

## Section 5: Time Slot Management

**Q: How does time slot management work?**

A: Providers create time slots from the Manage Slots page. They can create a slot one at a time (choosing a date, start time, and end time), or they can create slots in batch by specifying a date range and a time interval. Each slot has a status: available or booked.

---

**Q: How does a customer view available slots?**

A: On the service detail page, the customer can see available time slots for that service. The frontend calls GET /slots?service_id=X and the backend returns only the slots with status=available that belong to that service's provider.

---

**Q: What happens to a slot when it is booked?**

A: When a customer books a slot, the backend sets the slot's status from available to booked. This happens in the same database transaction as creating the booking record, so both changes are committed together — either both succeed or both fail.

---

## Section 6: Booking Logic and Conflict Prevention

**Q: How does your system prevent two customers from booking the same slot?**

A: Before creating a booking, the backend uses a database row lock — SELECT FOR UPDATE — on the slot. This locks the slot row so no other transaction can modify it at the same time. Then it checks if the slot status is still available. If it is, it creates the booking and marks the slot as booked. If another request comes in for the same slot at the same time, it has to wait for the lock to be released, and by then the slot is already booked, so it gets rejected.

---

**Q: What error does the second customer get?**

A: The second customer gets a 400 Bad Request error with a message like This slot is no longer available or a 409 Conflict error if there is a database constraint violation. The frontend shows this message to the user so they know to pick a different slot.

---

**Q: How did you test this concurrent booking prevention?**

A: I wrote a test called test_simultaneous_booking_conflict_prevention that uses Python's asyncio.gather() to fire two booking requests for the same slot at exactly the same time. The test verifies that exactly one request succeeds with a 201 status and the other fails with 400 or 409. This test passes reliably.

---

**Q: What happens when a customer cancels a booking?**

A: When a customer cancels, the backend sets two things atomically in one database transaction: the booking status changes to cancelled, and the slot status changes back to available. Because both changes are in the same transaction, there is no risk of one succeeding and the other failing.

---

**Q: Can a cancelled slot be rebooked?**

A: Yes. Once the slot is back to available status, any customer can book it again. The old cancelled booking record remains in the database for history — it is not deleted. A new booking record is created for the new customer.

---

## Section 7: Technical Decisions and Challenges

**Q: What was the hardest part of this project?**

A: The most challenging part was getting the time slot availability query right. Slots can be directly assigned to a service, or they can be unassigned provider slots. When a customer looks for slots for a particular service, the backend needs to find both the service-specific slots and the unassigned provider slots. I had to write a query that handles both cases correctly.

---

**Q: Did you face any bugs or issues during development?**

A: Yes, a few. First, Tailwind CSS was not compiling because the PostCSS config file (postcss.config.js) was missing — I created it and that fixed the styling. Second, bcrypt version 5.x is incompatible with the passlib library, so I pinned bcrypt to version 4.0.1. Third, SQLite stores datetimes without timezone info, so I had to make sure the backend uses naive datetimes (without timezone) throughout to avoid comparison errors.

---

**Q: How is the frontend and backend connected?**

A: They are completely separate. The frontend is a React SPA running on port 5173. The backend is a FastAPI server running on port 8000. The frontend calls the backend via HTTP using Axios. CORS is configured on the backend to allow requests from the frontend's origin.

---

**Q: How do you handle CORS?**

A: FastAPI's built-in CORSMiddleware is added to the app. It is configured to allow requests from http://localhost:5173 (the frontend's URL), allow all HTTP methods, and allow the Authorization header. Without this, the browser would block the frontend from calling the backend.

---

## Section 8: CRUD and Relationships

**Q: Explain the CRUD operations in your project.**

A: CRUD stands for Create, Read, Update, Delete. For services: providers can Create a service, Read (list/view) services, Update a service, and Delete a service. For time slots: providers Create slots, Read their slots, and Delete slots. For bookings: customers Create a booking (book a slot), Read their bookings (history), and Cancel a booking (soft-update, not delete). All operations go through the REST API.

---

**Q: What is a soft delete?**

A: A soft delete means the record is not actually removed from the database. Instead, a flag is set to mark it as inactive or cancelled. For example, cancelling a booking sets its status to cancelled but the booking record remains. This preserves history. Services also use an is_active flag for soft deletion.

---

## Section 9: Testing

**Q: How did you test your project?**

A: I wrote automated tests using Pytest and httpx. The tests use an in-memory SQLite database so they do not affect the real data. I have 10 tests covering: user registration, duplicate email prevention, login and JWT verification, service creation with role checks, booking creation, double-booking prevention, simultaneous booking conflict, and cancellation with slot release.

---

**Q: What is the purpose of the conftest.py file?**

A: conftest.py is where Pytest fixtures are defined. In this project, it sets up a fresh in-memory SQLite database for each test and provides an async HTTP client (httpx.AsyncClient) connected to the FastAPI app. Each test starts with a clean database, so tests are isolated and do not interfere with each other.

---

## Section 10: Personal Contribution Questions

**Q: What did you personally work on?**

A: I built the entire project — both the backend and the frontend. On the backend, I designed the database schema, wrote the FastAPI routes, implemented JWT authentication, business logic for booking and slot management, and the concurrency protection using row-level locking. On the frontend, I built all the pages and components using React, wired up the API calls, and handled role-based routing so customers and providers see different views.

---

**Q: What would you improve if you had more time?**

A: I would add email notifications for booking confirmations and cancellations. I would also add a calendar view for providers to visualize their availability, and customer ratings and reviews for services. For production, I would switch from SQLite to PostgreSQL and add proper deployment configuration.

---

**Q: What did you learn from building this project?**

A: I learned how to build a full-stack web application with a completely decoupled backend and frontend. I learned how JWT authentication works in practice, how to use async SQLAlchemy, and most importantly, how to prevent race conditions in a booking system using database row-level locking. Testing concurrent scenarios with asyncio.gather was also a new and interesting challenge.

---
