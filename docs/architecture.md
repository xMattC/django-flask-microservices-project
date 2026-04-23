
# Architecture

## Overview

The system follows a microservice architecture with a Django backend-for-frontend (BFF) layer.

Each service is independently deployable and owns its own data.

---

## Services

### Django (Web / BFF) (Planned)

Responsibilities:

- User authentication
- Session management
- Routing user requests
- Aggregating responses from services

---

### Projects Service (Planned)

Responsibilities:

- Project CRUD
- Project lifecycle (active / archived)
- Ownership validation

---

### Time Tracking Service (Planned)

Responsibilities:

- Clock-in / clock-out
- Time entry management
- Prevent overlapping sessions

---

### Tasks Service (Planned)

Responsibilities:

- Task creation and updates
- Task status (todo, started, completed)
- Project-task relationships

---

### Metrics Service (Planned)

Responsibilities:

- Aggregated reporting
- Time summaries
- Productivity insights

---

## Communication

Services communicate via HTTP APIs.

Example flow:

User → Django → Projects Service → Time Tracking Service

---

## Data Ownership

Each service has its own database.

- No cross-service foreign keys
- Relationships handled via IDs
- Data consistency maintained via API validation

---

## Project Deletion Strategy

Projects are soft-deleted:

- Marked as archived in Projects Service
- Tasks and time entries excluded from normal queries
- Historical data preserved

---

## Deployment Model

- Docker-based services
- Reverse proxy routes traffic
- CI/CD pipeline handles deployment

---

## Future Architecture Improvements

- Event-driven messaging (project.deleted events)
- Service-to-service async communication
- Observability improvements (metrics, tracing)