import json

import requests
import responses
from django.test import SimpleTestCase, override_settings

from clients.tasks_service import (
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
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
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
                    "owner_user_id": "123",
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
        self.assertEqual(json.loads(request.body), request_payload)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_tasks
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_a_task
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for edit_a_task
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for delete_a_task
    # -----------------------------------------------------------------------------------------------------------------
