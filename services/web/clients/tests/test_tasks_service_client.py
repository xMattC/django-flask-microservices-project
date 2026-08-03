import json

import requests
import responses
from django.test import SimpleTestCase, override_settings

from clients.tasks_service_client import (
    TasksServiceError,
    TasksServiceUnavailable,
    create_task,
    delete_a_task,
    edit_a_task,
    get_a_task,
    get_tasks,
)


class TasksClientTests(SimpleTestCase):
    """Test Tasks service client.

    Service Client Test Coverage Checklist:
    - Happy path returns expected data
    - Required headers are sent (e.g. auth / X-User-ID)
    - Network failures raise ServiceUnavailable
    - Upstream 4xx/5xx responses raise ServiceError
    - Invalid JSON responses raise ServiceError
    - Response structure is validated
    - Incorrect data types are rejected
    """

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for create_task
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_create_task_sends_user_id_header_payload_and_returns_a_task_entry(self):
        """Test create_task calls upstream with user header, payload, and returns one task entry."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }
        mock_response_payload = {
            "results": [
                {
                    "id": 0,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "task_name": "Task-1",
                    "description": "Get Milk",
                    "state": "to-do",
                    "created_at": "2026-05-07T06:43:30.504Z",
                    "updated_at": "2026-05-07T06:43:30.504Z",
                }
            ]
        }
        responses.add(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            json=mock_response_payload,
            status=201,
        )

        result = create_task(user_id=user_id, payload=request_payload)

        self.assertEqual(result, mock_response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(request.body), request_payload) # type: ignore

    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_create_task_raises_service_unavailable_on_request_exception(self):
        """Test create_task raises TasksServiceUnavailable on network failure."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            callback=raise_error,
        )

        with self.assertRaises(TasksServiceUnavailable):
            create_task(user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_create_task_raises_error_on_non_2xx_response(self):
        """Test create_task raises TasksServiceError on a non-2xx response."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }

        responses.add(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TasksServiceError):
            create_task(user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_create_task_raises_error_on_invalid_json_response(self):
        """Test create_task raises TasksServiceError on invalid JSON."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }

        responses.add(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            body="Not JSON",
            status=201,
            content_type="text/plain",
        )

        with self.assertRaises(TasksServiceError):
            create_task(user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_create_task_raises_error_when_results_key_missing(self):
        """Test create_task raises TasksServiceError when results is missing."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }

        responses.add(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            json={"unexpected_key": []},
            status=201,
        )

        with self.assertRaises(TasksServiceError):
            create_task(user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_create_task_raises_error_when_results_is_not_list(self):
        """Test create_task raises TasksServiceError when results is not a list."""
        user_id = 123
        request_payload = {
            "project_id": 42,
            "task_name": "Task-1",
            "description": "Get Milk",
            "state": "to-do",
        }

        responses.add(
            method=responses.POST,
            url="http://tasks:5000/api/tasks",
            json={"results": "not a list"},
            status=201,
        )

        with self.assertRaises(TasksServiceError):
            create_task(user_id=user_id, payload=request_payload)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_tasks
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TASKS_SERVICE_URL="http://tasks:5000")
    def test_get_tasks_returns_results_list(self):
        """Test get_tasks sends the user header and returns task results."""
        user_id = 123

        mock_response_payload = {
            "results": [
                {
                    "id": 1,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "task_name": "Task-1",
                    "description": "Get Milk",
                    "state": "to-do",
                    "created_at": "2026-05-07T06:43:30.504Z",
                    "updated_at": "2026-05-07T06:43:30.504Z",
                }
            ]
        }
        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks",
            json=mock_response_payload,
            status=200,
        )

        result = get_tasks(user_id=user_id)
        self.assertEqual(result, mock_response_payload["results"])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.url, "http://tasks:5000/api/tasks")
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))


    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_get_tasks_sends_user_id_header(self):
        """Test get_tasks sends X-User-ID header."""
        user_id = 123
        mock_response_payload = {"results": []}
        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks",
            json=mock_response_payload,
            status=200,
        )

        get_tasks(user_id=user_id)

        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_tasks_sends_query_params(self):
        """Test get_tasks sends query parameters."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks?project_id=42",
            json={"results": []},
            status=200,
        )

        get_tasks(user_id=user_id, project_id=42)

        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertIn("project_id=42", request.url) # type: ignore

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_get_tasks_raises_service_unavailable_on_request_exception(self):
        """Test get_tasks raises TasksServiceUnavailable on request exception."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks",
            body=requests.RequestException("Network error"),
            status=500,
        )

        with self.assertRaises(TasksServiceUnavailable):
            get_tasks(user_id=user_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_get_tasks_raises_error_on_non_2xx_response(self):
        """Test get_tasks raises TasksServiceError on 4xx/5xx response."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TasksServiceError):
            get_tasks(user_id=user_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_get_tasks_raises_error_on_invalid_response_schema(self):
        """Test get_tasks raises TasksServiceError when response schema is invalid."""
        user_id = 123
        mock_response_payload = {"unexpected_key": []}

        responses.add(
            method=responses.GET,
            url="http://tasks:5000/api/tasks",
            json=mock_response_payload,
            status=200,
        )

        with self.assertRaises(TasksServiceError):
            get_tasks(user_id=user_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_a_task
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://tasks:5000")
    def test_get_task_returns_a_task(self):
        """Test get_tasks returns a single time entry."""
        user_id = 123
        task_id = 10

        mock_response_payload = {
            "results": [
                {
                    "id": task_id,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "task_name": "Task-1",
                    "description": "Get Milk",
                    "state": "to-do",
                    "created_at": "2026-05-07T06:43:30.504Z",
                    "updated_at": "2026-05-07T06:43:30.504Z",
                }
            ]
        }

        responses.add(
            method=responses.GET,
            url=f"http://tasks:5000/api/tasks/{task_id}",
            json=mock_response_payload,
            status=200,
        )

        result = get_a_task(user_id=user_id, task_id=task_id)

        self.assertEqual(result, mock_response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertEqual(request.url, f"http://tasks:5000/api/tasks/{task_id}")
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for edit_a_task
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for delete_a_task
    # -----------------------------------------------------------------------------------------------------------------
