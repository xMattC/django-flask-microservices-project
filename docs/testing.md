# Testing

This project uses automated tests to verify business behaviour, user isolation, service boundaries, deployment reliability, and system workflows across the microservices platform.

The test suite is grouped into four practical layers:

- Unit tests
- Integration tests
- System tests
- Smoke tests

---

## Unit Tests

Unit tests validate isolated logic within a single service.

Examples include:

- Form validation
- Model methods
- Schema validation
- Helper functions
- Business rules
- Management commands

---

## Integration Tests

Integration tests validate multiple components working together.

This includes:

- Django view and route behaviour
- Flask API endpoint behaviour
- Service client behaviour
- Database-backed API workflows
- API contract and JSON response validation
- Required request headers such as `X-User-ID`

---

## System Tests

System tests validate complete user workflows across the platform.

Examples include:

- User logs in
- User creates a project
- User starts a time-tracking session
- User stops the session
- Dashboard reflects the updated state

---

## Smoke Tests

Smoke tests validate that the deployed stack starts and responds correctly.

Examples include:

- Service health checks
- Application startup validation
- Basic deployment verification
- Database connectivity checks

---

# Architectural Guarantees

The following guarantees are enforced through application logic and validated through automated tests.

## Authentication

- Protected routes require authentication through the Django BFF
- Authentication state is managed centrally by Django
- User identity is propagated using `X-User-ID`
- Backend services do not manage independent authentication systems

## User Isolation

- Resources are scoped to individual users
- Users can only access their own projects and time entries
- Cross-user access is rejected
- Ownership rules are enforced consistently

## Service Boundaries

- Services own their own business logic and persistence
- Services communicate exclusively through HTTP APIs
- Services remain independently deployable
- The Django BFF coordinates user-facing workflows

## API Guarantees

- APIs return consistent JSON structures
- Validation failures return appropriate HTTP status codes
- Missing user context is rejected
- Service failures are handled gracefully

---

# Continuous Verification

The project uses continuous verification during development and deployment.

This includes:

- Local automated test execution
- Docker-based test execution
- CI pipeline execution
- Deployment smoke tests

---

# Test File Reference

## Unit Tests

Web Service: [`test_app_forms.py`](../services/web/app/tests/test_app_forms.py)

Web Service: [`test_user_forms.py`](../services/web/user/tests/test_user_forms.py)

Web Service: [`test_user_models.py`](../services/web/user/tests/test_user_models.py)

Web Service: [`test_commands.py`](../services/web/common/tests/test_commands.py)

Projects Service: [`test_schemas.py`](../services/projects/tests/test_schemas.py)

Projects Service: [`test_model.py`](../services/projects/tests/test_model.py)

Time Tracking Service: [`test_model.py`](../services/time-tracking/tests/test_model.py)

Time Tracking Service: [`test_schemas.py`](../services/time-tracking/tests/test_schemas.py)

---

## Integration Tests

Web Service: [`test_app_dashboard_view.py`](../services/web/app/tests/views/test_app_dashboard_view.py)

Web Service: [`test_app_home_view.py`](../services/web/app/tests/views/test_app_home_view.py)

Web Service: [`test_app_projects_view.py`](../services/web/app/tests/views/test_app_projects_view.py)

Web Service: [`test_app_time_tracking_views.py`](../services/web/app/tests/views/test_app_time_tracking_views.py)

Web Service: [`test_user_api.py`](../services/web/user/tests/test_user_api.py)

Web Service: [`test_projects_service_client.py`](../services/web/clients/tests/test_projects_service_client.py)

Web Service: [`test_time_tracking_service_client.py`](../services/web/clients/tests/test_time_tracking_service_client.py)

Projects Service: [`test_api.py`](../services/projects/tests/test_api.py)

Projects Service: [`test_health.py`](../services/projects/tests/test_health.py)

Projects Service: [`test_contract.py`](../services/projects/tests/test_contract.py)

Projects Service: [`test_integration.py`](../services/projects/tests/test_integration.py)

Time Tracking Service: [`test_api.py`](../services/time-tracking/tests/test_api.py)

Time Tracking Service: [`test_health.py`](../services/time-tracking/tests/test_health.py)

Time Tracking Service: [`test_contract.py`](../services/time-tracking/tests/test_contract.py)

Time Tracking Service: [`test_integration.py`](../services/time-tracking/tests/test_integration.py)

---

## System Tests

Platform: [`system-test.sh`](../tests/system/run-system-tests.sh)

---

## Smoke Tests

Platform: [`smoke-tests.sh`](../tests/smoke/smoke-tests.sh)

---

# Summary

The automated test suite provides confidence that the platform:

- Enforces user isolation
- Preserves service boundaries
- Handles service communication correctly
- Maintains API consistency
- Supports reliable system workflows
- Remains maintainable as the architecture evolves
