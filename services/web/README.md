# Django BFF (Web Service)

## Overview

This service acts as the **Backend for Frontend (BFF)** for the platform.

It is responsible for:
- User authentication
- Session management
- Rendering UI templates
- Acting as the single entry point for the frontend
- Communicating with backend microservices

This service does **not** contain business logic for projects, tasks, or time tracking.

---

## Responsibilities

- User registration, login, logout
- Session-based authentication (cookies)
- Dashboard UI
- Project selection UI
- Clock-in / clock-out UI
- Task and reporting pages
- Forwarding requests to backend services

---

## Key Features

- Custom user model (email-based authentication)
- Django templates for frontend rendering
- Protected routes using `request.user`
- Service integration layer (API calls to microservices)

---

## Architecture Role

Browser → Django BFF → Microservices

Django handles:
- Authentication
- UI rendering
- Request routing

Microservices handle:
- Business logic
- Data storage

---

## Example Flow

1. User logs in
2. Django creates session
3. User accesses dashboard
4. Django calls backend services (e.g. time tracking)
5. Data is aggregated and rendered in templates

---

## Endpoints (Example)

- /login/
- /logout/
- /register/
- /dashboard/

