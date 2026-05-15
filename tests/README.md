# Testing Architecture

This project uses multiple layers of automated testing to validate business behaviour, service boundaries, deployment reliability, and full system workflows across the microservices platform. The testing structure is organised by responsibility to keep tests maintainable and scalable as the architecture evolves.

---

## Smoke Test
Smoke tests validate that the platform can build, start, and operate correctly as a complete deployment stack. Smoke test was designed to catch deployment and infrastructure issues before production deployment.

#### Test files:

- [`smoke-test.sh`](smoke/smoke-tests.sh)

---

## Integration Tests
Integration tests validate communication between services and ensure architectural boundaries behave correctly. Tests  designed to simulate realistic service interactions without requiring full end-to-end user workflows.

#### Test files:

- [`TODO`](integration/)

---

## System Tests
System tests validate complete user workflows across the entire platform. These tests simulate real application behaviour from the user perspective across multiple services. System tests provide confidence that the platform behaves correctly as a complete system.

#### Test files:

- [`TODO`](system/)

---

## Unit & API Tests - Web Service

The Django web service acts as the Backend-for-Frontend (BFF) layer, handling authentication, session management, template rendering, user workflows, and orchestration of backend microservices.

The test suite focuses on validating user-facing behaviour and service orchestration rather than framework internals.

#### Test Files:

- [`test_app_forms.py`](../services/web/app/tests/test_app_forms.py)
- [`test_app_dashboard_view.py`](../services/web/app/tests/views/test_app_dashboard_view.py)
- [`test_app_home_view.py`](../services/web/app/tests/views/test_app_home_view.py)
- [`test_app_projects_view.py`](../services/web/app/tests/views/test_app_projects_view.py)
- [`test_app_time_tracking_views.py`](../services/web/app/tests/views/test_app_time_tracking_views.py)
- [`test_projects_service_client.py`](../services/web/clients/tests/test_projects_service_client.py)
- [`test_time_tracking_service_client.py`](../services/web/clients/tests/test_time_tracking_service_client.py)
- [`test_commands.py`](../services/web/common/tests/test_commands.py)
- [`test_user_api.py`](../services/web/user/tests/test_user_api.py)
- [`test_user_forms.py`](../services/web/user/tests/test_user_forms.py)
- [`test_user_models.py`](../services/web/user/tests/test_user_models.py)

---

## Unit & API Tests - Projects Service

The Projects service manages project creation, ownership, and project lifecycle operations. The test suite focuses on ensuring that project management behaviour remains consistent, user-isolated, and reliable across API and persistence workflows.

#### Test Files:

- [`test_projects_health.py`](../services/projects/tests/test_projects_health.py)
- [`test_projects_api.py`](../services/projects/tests/test_projects_api.py)
- [`test_projects_schemas.py`](../services/projects/tests/test_projects_schemas.py)

---

## Unit & API Tests -  Time Tracking Service

The Time Tracking service manages time entry workflows, active tracking sessions, and project-associated work logs.

The test suite focuses on ensuring that time tracking workflows remain consistent, isolated per user, and reliable across different usage scenarios.

#### Test Files:

- [`test_time_entry_health.py`](../services/time-tracking/tests/test_time_entry_health.py)
- [`test_time_entry_model.py`](../services/time-tracking/tests/test_time_entry_model.py)
- [`test_time_entry_api.py`](../services/time-tracking/tests/test_time_entry_api.py)
- [`test_time_entry_schemas.py`](../services/time-tracking/tests/test_time_entry_schemas.py)

---

## Unit & API Tests - Tasks Service

The Tasks service manages task creation, organisation, and task lifecycle workflows. The test suite focuses on ensuring that task management behaviour remains consistent, user-isolated, and reliable across different usage scenarios.

#### Test Files:

- [`test_tasks_health.py` - TODO]
- [`test_tasks_model.py`- TODO]
- [`test_tasks_api.py`- TODO]
- [`test_tasks_schemas.py`- TODO]

---