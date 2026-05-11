# Architecture Design Document

This document describes the architecture of the Productivity Microservices Platform, a backend engineering portfolio project built using Django, Flask, PostgreSQL, and Docker.

The system follows a microservice architecture with a Django backend-for-frontend (BFF) layer.

Each service is independently deployable and owns its own data.

---

## 1. System Overview

The platform is designed as a multi-service backend application for productivity workflows such as:

- Project management
- Time tracking
- Future task management services

The system uses:

- Django as the main web/BFF service
- Flask microservices for domain-specific APIs
- PostgreSQL databases per service
- Docker Compose for local orchestration

---

## 2. High-Level Architecture

![System Architecture](architecture-diagram.png)


The Django service acts as the entry point for users and communicates with downstream Flask services over HTTP.

Each service owns its own database, migrations, and business logic.

---

## 3. Services

| Service | Responsibility |
|---|---|
| Django Web Service | Authentication, session handling, frontend orchestration |
| Projects Service | Project CRUD operations |
| Time Tracking Service | Time entry and tracking workflows |
| PostgreSQL Databases | Persistent storage per service |

---

## 4. Backend-for-Frontend (BFF)

The Django web service follows a Backend-for-Frontend approach.

Responsibilities include:

- User authentication
- Session management
- Rendering web pages
- Calling downstream services
- Passing authenticated user context
- Handling service responses

This keeps browser-facing logic separate from domain-specific APIs.

---

## 5. Service Communication

Services communicate using HTTP requests.

The Django service sends requests to Flask services using internal Docker service URLs configured through environment variables.

Example request flow:

```text
User Request
    │
    ▼
Django Web Service
    │
    ▼
Flask Microservice
    │
    ▼
PostgreSQL Database
```

The Django service passes the authenticated user identity using the `X-User-ID` request header.

---

## 6. Authentication and Permissions

Authentication is handled by Django using built-in session-based authentication.

Flask services do not manage browser sessions directly.

Permissions are enforced through:

- Protected Django views
- User-scoped service requests
- `X-User-ID` ownership checks
- Database queries filtered by user ID

This ensures users only access their own data.

---

## 7. Data Ownership

Each service owns its own database and migrations.

Benefits of this approach include:

- Clear service boundaries
- Reduced coupling between services
- Independent schema changes
- Easier future scaling

Current ownership model:

```text
Projects Service
   └── Project data

Time Tracking Service
   └── Time entry data
```

---

## 8. Validation and Testing

Validation is handled at the service level.

The platform includes:

- Request validation using Marshmallow schemas
- Automated API and model tests
- flake8 linting
- GitHub Actions CI workflows

Common handled responses include:

- `400 Bad Request`
- `404 Not Found`
- `5xx Service Error`

---

## 9. Local Development and Deployment

The platform uses Docker Compose for local development.

Containers include:

- Django web service
- Flask services
- PostgreSQL databases

Deployment currently focuses on:

- Docker-based hosting
- Environment variable configuration
- AWS EC2 deployment workflows

The infrastructure is intentionally lightweight for portfolio demonstration purposes.

---

## 10. Future Improvements

Planned future improvements include:

- Tasks microservice
- JWT-based service authentication
- API versioning
- Centralised logging
- Metrics and observability
- Asynchronous service communication
- Deployment automation
- Container orchestration with Kubernetes or ECS

---

## Summary

The Productivity Microservices Platform demonstrates:

- Django and Flask interoperability
- Backend-for-Frontend architecture
- Service-oriented backend design
- Independent service ownership
- Docker-based development workflows
- Automated testing and CI practices

The project is designed to showcase practical backend engineering skills in a multi-service environment.

- Event-driven messaging (project.deleted events)
- Service-to-service async communication
- Observability improvements (metrics, tracing)
