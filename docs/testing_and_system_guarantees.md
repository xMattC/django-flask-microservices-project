# Testing and System Guarantees

This project uses automated tests to verify service behaviour, user isolation, and inter-service communication across the microservices architecture.

The test suite focuses on validating business behaviour rather than framework internals.

---

# Test Strategy

The project uses multiple layers of testing to validate both isolated components and full system workflows.

---

## Unit Tests

Unit tests validate isolated logic within a single service.

Examples include:

- form validation logic
- model methods
- helper functions
- business rules
- password handling
- ownership validation
- utility functions

Unit tests avoid external dependencies where possible and focus on deterministic behaviour.

---

## View and Route Tests

Django view tests verify application behaviour from the user perspective.

These tests cover:

- authentication requirements
- redirects
- rendered templates
- form submission handling
- session behaviour
- error messaging
- protected routes

Simple framework wiring such as static URL definitions or admin configuration is generally not tested directly.

---

## API / Service Tests

API tests validate individual backend services through HTTP interfaces.

These tests verify:

- request and response behaviour
- validation rules
- filtering and ownership enforcement
- database persistence
- error handling
- response consistency

Each service is tested independently as an isolated boundary.

---

## Integration Tests (TODO!)

Integration tests verify communication between services.

Examples include:

- Django BFF calling backend APIs
- request forwarding
- `X-User-ID` propagation
- handling downstream failures
- aggregation of backend responses

These tests ensure service boundaries behave correctly under realistic conditions.

---

## System (End-to-End) Tests (TODO!)

System tests validate complete user workflows across the architecture.

Examples include:

- user registration and authentication
- project management workflows
- clock in / clock out flows
- dashboard rendering
- multi-service interaction paths

These tests simulate real user behaviour across the full stack.

---

# Architectural Guarantees

The following guarantees are enforced by application logic and verified through automated tests.

---

## Authentication

- Protected routes require authentication through the Django BFF
- Authentication state is managed centrally by Django
- User identity is propagated to backend services through request headers
- Backend services do not manage independent authentication systems

---

## User Isolation

- All resources are scoped to a specific user
- Users can only access their own projects and time entries
- Cross-user access is rejected
- Ownership checks are enforced consistently across services

---

## Service Boundaries

- Each service owns its own business logic and persistence layer
- Services communicate exclusively through HTTP APIs
- Backend services remain independently deployable
- The Django BFF coordinates user-facing workflows

---

## Projects Service Guarantees

- Users can create, update, view, and delete their own projects
- Project queries return only user-owned records
- Project ownership cannot be reassigned between users

---

## Time Tracking Guarantees

- Users can only have one active running session at a time
- Clock-in creates an active session
- Clock-out completes the session
- Sessions remain associated with a project through `project_id`
- Dashboard aggregation reflects current tracking state correctly

---

## API Guarantees

- APIs return consistent JSON structures
- Validation failures return appropriate HTTP status codes
- Missing or invalid user context is rejected
- Service failures are handled gracefully by the BFF layer

---

# Continuous Verification

The project uses continuous verification during development and deployment.

This includes:

- local automated test execution
- Docker-based integration testing
- CI pipeline test execution
- isolated service testing

---

# Testing Philosophy

The project prioritises testing business behaviour and architectural guarantees over framework implementation details.

Tests focus on:

- user-facing behaviour
- service contracts
- isolation guarantees
- business rules
- communication correctness

The project generally avoids unnecessary testing of:

- framework boilerplate
- static configuration
- declarative admin setup
- simple URL mappings without logic

---

# Summary

The automated test suite ensures the system:

- enforces strict user-level isolation
- maintains clear service ownership boundaries
- correctly handles inter-service communication
- provides predictable API behaviour
- supports reliable end-to-end user workflows
- remains maintainable as the architecture evolves

This provides confidence that the system behaves as a stable and predictable microservices architecture.
