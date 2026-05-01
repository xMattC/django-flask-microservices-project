# Testing Strategy and System Guarantees

This project uses automated tests to verify both individual services and full system behaviour across the microservices architecture.

The test suite ensures correct service boundaries, data isolation, and reliable communication between services.

---

## Test Layers

### Unit Tests

Unit tests validate isolated logic within a service:

- model logic and helpers  
- validation functions  
- derived calculations  

These tests ensure internal logic behaves correctly in isolation.

---

### API / Service Tests

API tests validate a single service via HTTP:

- request/response behaviour  
- validation and error handling  
- database interaction  
- ownership and filtering  

These tests simulate real usage of each microservice independently.

---

### Integration Tests

Integration tests verify communication between components:

- Django BFF calling backend services  
- header propagation (e.g. `X-User-ID`)  
- handling of downstream responses and errors  

These tests ensure services interact correctly.

---

### System (End-to-End) Tests

System tests verify full user workflows across services:

- user authentication via Django  
- project creation  
- clock in / clock out flows  
- dashboard data aggregation  

These tests simulate real user behaviour across the entire system.

---

## System Guarantees

The following guarantees are enforced by application logic and verified by tests.

### Authentication

- All protected routes require authentication via Django BFF  
- User context is passed to services via headers  
- Services rely on BFF for authentication, not internal auth logic  

---

### Ownership and Data Isolation

- All resources are scoped to `user_id`  
- Users can only access their own projects and sessions  
- Cross-user access is not permitted  
- Invalid access returns appropriate error responses  

---

### Service Boundaries

- Each service owns its domain logic and data  
- No business logic is shared between services  
- Services communicate only via HTTP APIs  

---

### Projects Service

- Users can create, view, update, and delete their own projects  
- Project lists return only user-owned data  
- Project ownership cannot be reassigned  

---

### Time Tracking Service

- Users can only have one active session at a time  
- Clock-in creates a new active session  
- Clock-out completes the session and records duration  
- Sessions are linked to projects via `project_id`  

---

### API Behaviour

- All endpoints return consistent JSON responses  
- Invalid requests return appropriate error codes  
- Missing or invalid user context is rejected  
- Service failures are handled gracefully by Django BFF  

---

## Continuous Verification

- Tests are run locally during development  
- CI executes tests on each change  
- Docker environment is used for system-level testing  

---

## Summary

The test suite verifies that the system:

- enforces strict user-level data isolation  
- maintains clear service boundaries  
- correctly handles inter-service communication  
- provides consistent and reliable API behaviour  
- supports real user workflows across services  

This ensures the system behaves as a predictable and maintainable microservices architecture.
