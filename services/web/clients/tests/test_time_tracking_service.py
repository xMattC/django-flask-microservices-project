import requests
import responses
import json
from django.test import SimpleTestCase, override_settings

from clients.time_tracking_service import (
    TimeTrackingServiceError,
    TimeTrackingServiceUnavailable,
    create_time_entry,
    get_time_entries,
    get_time_entry,
    stop_time_entry,
    update_time_entry,
)


class TimeTrackingClientTests(SimpleTestCase):
    """Test Time Tracking service client.

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
    # Test cases for create_time_entry
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_create_time_entry_sends_user_id_header_payload_and_returns_time_entry(self):
        """Test create_time_entry calls upstream with user header, payload, and returns one time entry."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}
        mock_response_payload = {
            "results": [
                {
                    "id": 0,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "description": "Test",
                    "started_at": "2026-05-07T06:43:30.504Z",
                    "ended_at": "2026-05-07T06:43:30.504Z",
                    "duration_seconds": 0,
                    "created_at": "2026-05-07T06:43:30.504Z",
                    "updated_at": "2026-05-07T06:43:30.504Z",
                }
            ]
        }
        responses.add(
            method=responses.POST,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=201,
        )

        result = create_time_entry(user_id=user_id, payload=request_payload)

        self.assertEqual(result, mock_response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(request.body), request_payload)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_create_time_entry_raises_service_unavailable_on_request_exception(self):
        """Test create_time_entry raises TimeTrackingServiceUnavailable on network failure."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.POST,
            url="http://time-tracking:5000/api/time-entries",
            callback=raise_error,
        )

        with self.assertRaises(TimeTrackingServiceUnavailable):
            create_time_entry(user_id=user_id, payload=request_payload)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_create_time_entry_raises_error_on_non_2xx_response(self):
        """Test create_time_entry raises TimeTrackingServiceError on 4xx/5xx response."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://time-tracking:5000/api/time-entries",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceError):
            create_time_entry(user_id=user_id, payload=request_payload)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_create_time_entry_raises_error_on_invalid_json_response(self):
        """Test create_time_entry raises TimeTrackingServiceError on invalid JSON response."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}

        with responses.RequestsMock() as rsps:
            rsps.add(
                method=responses.POST,
                url="http://time-tracking:5000/api/time-entries",
                body="Not a JSON",
                status=201,
            )

            with self.assertRaises(TimeTrackingServiceError):
                create_time_entry(user_id=user_id, payload=request_payload)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_create_time_entry_raises_error_when_results_key_missing(self):
        """Test create_time_entry raises TimeTrackingServiceError when 'results' key is missing."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}
        mock_response_payload = {"unexpected_key": []}

        responses.add(
            method=responses.POST,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=201,
        )

        with self.assertRaises(TimeTrackingServiceError):
            create_time_entry(user_id=user_id, payload=request_payload)

    def test_create_time_entry_raises_error_when_results_is_not_list(self):
        """Test create_time_entry raises TimeTrackingServiceError when 'results' is not a list."""
        user_id = 123
        request_payload = {"project_id": 42, "description": "Test"}
        mock_response_payload = {"results": "not a list"}

        responses.add(
            method=responses.POST,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=201,
        )

        with self.assertRaises(TimeTrackingServiceError):
            create_time_entry(user_id=user_id, payload=request_payload)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_time_entries
    # -----------------------------------------------------------------------------------------------------------------

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entries_returns_results_list(self):
        """Test get_time_entries returns list of time entries."""
        user_id = 123

        mock_response_payload = {
            "results": [
                {
                    "id": 10,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "description": "Test",
                    "started_at": "2026-05-07T08:36:59.971Z",
                    "ended_at": "2026-05-07T08:36:59.971Z",
                    "duration_seconds": 0,
                    "created_at": "2026-05-07T08:36:59.971Z",
                    "updated_at": "2026-05-07T08:36:59.971Z",
                }
            ]
        }

        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=200,
        )

        result = get_time_entries(user_id=user_id)

        self.assertEqual(result, mock_response_payload["results"])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertEqual(request.url, "http://time-tracking:5000/api/time-entries")
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entries_sends_user_id_header(self):
        """Test get_time_entries sends X-User-ID header."""
        user_id = 123
        mock_response_payload = {"results": []}
        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=200,
        )

        get_time_entries(user_id=user_id)

        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entries_sends_query_params(self):
        """Test get_time_entries sends query parameters."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries?project_id=42&running_only=true",
            json={"results": []},
            status=200,
        )

        get_time_entries(
            user_id=user_id,
            project_id=42,
            running_only=True,
        )

        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertIn("project_id=42", request.url)
        self.assertIn("running_only=true", request.url)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entries_raises_service_unavailable_on_request_exception(self):
        """Test get_time_entries raises TimeTrackingServiceUnavailable on request exception."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries",
            body=requests.RequestException("Network error"),
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceUnavailable):
            get_time_entries(user_id=user_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entries_raises_error_on_non_2xx_response(self):
        """Test get_time_entries raises TimeTrackingServiceError on 4xx/5xx response."""
        user_id = 123

        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceError):
            get_time_entries(user_id=user_id)

    def test_get_time_entries_raises_error_on_invalid_response_schema(self):
        """Test get_time_entries raises TimeTrackingServiceError when response schema is invalid."""
        user_id = 123
        mock_response_payload = {"unexpected_key": []}

        responses.add(
            method=responses.GET,
            url="http://time-tracking:5000/api/time-entries",
            json=mock_response_payload,
            status=200,
        )

        with self.assertRaises(TimeTrackingServiceError):
            get_time_entries(user_id=user_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_time_entry
    # -----------------------------------------------------------------------------------------------------------------

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entry_returns_time_entry(self):
        """Test get_time_entry returns a single time entry."""
        user_id = 123
        time_entry_id = 10

        mock_response_payload = {
            "results": [
                {
                    "id": time_entry_id,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "description": "Test",
                    "started_at": "2026-05-07T08:36:59.971Z",
                    "ended_at": "2026-05-07T08:36:59.971Z",
                    "duration_seconds": 0,
                    "created_at": "2026-05-07T08:36:59.971Z",
                    "updated_at": "2026-05-07T08:36:59.971Z",
                }
            ]
        }

        responses.add(
            method=responses.GET,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json=mock_response_payload,
            status=200,
        )

        result = get_time_entry(user_id=user_id, time_entry_id=time_entry_id)

        self.assertEqual(result, mock_response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertEqual(request.url, f"http://time-tracking:5000/api/time-entries/{time_entry_id}")
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entry_sends_user_id_header(self):
        """Test get_time_entry sends X-User-ID header."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.GET,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json={"results": [{}]},
            status=200,
        )

        get_time_entry(user_id=user_id, time_entry_id=time_entry_id)

        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request

        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entry_raises_service_unavailable_on_request_exception(self):
        """Test get_time_entry raises TimeTrackingServiceUnavailable on request exception."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.GET,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            body=requests.RequestException("Connection error"),
        )

        with self.assertRaises(TimeTrackingServiceUnavailable):
            get_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entry_raises_error_on_non_2xx_response(self):
        """Test get_time_entry raises TimeTrackingServiceError on 4xx/5xx response."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.GET,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceError):
            get_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_get_time_entry_raises_error_on_invalid_response_schema(self):
        """Test get_time_entry raises TimeTrackingServiceError on invalid response schema."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.GET,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json={"unexpected_key": []},
            status=200,
        )

        with self.assertRaises(TimeTrackingServiceError):
            get_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for stop_time_entry
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_stop_time_entry_returns_time_entry(self):
        """Test stop_time_entry returns the stopped time entry."""
        user_id = 123
        time_entry_id = 10

        mock_response_payload = {
            "results": [
                {
                    "id": time_entry_id,
                    "owner_user_id": user_id,
                    "project_id": 42,
                    "description": "Test",
                    "started_at": "2026-05-07T08:36:59.971Z",
                    "ended_at": "2026-05-07T09:36:59.971Z",
                    "duration_seconds": 3600,
                    "created_at": "2026-05-07T08:36:59.971Z",
                    "updated_at": "2026-05-07T09:36:59.971Z",
                }
            ]
        }

        responses.add(
            method=responses.POST,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}/stop",
            json=mock_response_payload,
            status=200,
        )

        result = stop_time_entry(user_id=user_id, time_entry_id=time_entry_id)

        self.assertEqual(result, mock_response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_stop_time_entry_sends_user_id_header(self):
        """Test stop_time_entry sends X-User-ID header."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.POST,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}/stop",
            json={"results": [{}]},
            status=200,
        )

        stop_time_entry(user_id=user_id, time_entry_id=time_entry_id)

        request = responses.calls[0].request

        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_stop_time_entry_raises_service_unavailable_on_request_exception(self):
        """Test stop_time_entry raises TimeTrackingServiceUnavailable on request exception."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.POST,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}/stop",
            body=requests.RequestException("Connection error"),
        )

        with self.assertRaises(TimeTrackingServiceUnavailable):
            stop_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_stop_time_entry_raises_error_on_non_2xx_response(self):
        """Test stop_time_entry raises TimeTrackingServiceError on 4xx/5xx response."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.POST,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}/stop",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceError):
            stop_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_stop_time_entry_raises_error_on_invalid_response_schema(self):
        """Test stop_time_entry raises TimeTrackingServiceError on invalid response schema."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.POST,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}/stop",
            json={"unexpected_key": []},
            status=200,
        )

        with self.assertRaises(TimeTrackingServiceError):
            stop_time_entry(user_id=user_id, time_entry_id=time_entry_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for update_time_entry
    # -----------------------------------------------------------------------------------------------------------------
    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_update_time_entry_returns_time_entry(self):
        """Test update_time_entry returns the updated time entry."""
        user_id = 123
        time_entry_id = 10
        request_payload = {"description": "Updated"}
        mock_response_payload = {"results": [{"id": time_entry_id, "owner_user_id": user_id, "description": "Updated"}]}

        responses.add(
            method=responses.PATCH,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json=mock_response_payload,
            status=200,
        )

        result = update_time_entry(user_id=user_id, time_entry_id=time_entry_id, payload=request_payload)

        self.assertEqual(result, mock_response_payload["results"][0])

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_update_time_entry_sends_user_id_header_and_payload(self):
        """Test update_time_entry sends X-User-ID header and JSON payload."""
        user_id = 123
        time_entry_id = 10
        request_payload = {"description": "Updated"}

        responses.add(
            method=responses.PATCH,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json={"results": [{}]},
            status=200,
        )

        update_time_entry(user_id=user_id, time_entry_id=time_entry_id, payload=request_payload)

        request = responses.calls[0].request

        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertIsNotNone(request.body)
        self.assertEqual(json.loads(request.body), request_payload)

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_update_time_entry_raises_service_unavailable_on_request_exception(self):
        """Test update_time_entry raises TimeTrackingServiceUnavailable on request exception."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.PATCH,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            body=requests.RequestException("Connection error"),
        )

        with self.assertRaises(TimeTrackingServiceUnavailable):
            update_time_entry(user_id=user_id, time_entry_id=time_entry_id, payload={})

    @responses.activate
    @override_settings(TIME_TRACKING_SERVICE_URL="http://time-tracking:5000")
    def test_update_time_entry_raises_error_on_non_2xx_response(self):
        """Test update_time_entry raises TimeTrackingServiceError on 4xx/5xx response."""
        user_id = 123
        time_entry_id = 10

        responses.add(
            method=responses.PATCH,
            url=f"http://time-tracking:5000/api/time-entries/{time_entry_id}",
            json={"message": "Error"},
            status=500,
        )

        with self.assertRaises(TimeTrackingServiceError):
            update_time_entry(user_id=user_id, time_entry_id=time_entry_id, payload={})

    # def test_update_time_entry_raises_error_on_invalid_response_schema(self):
    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for delete_time_entry
    # -----------------------------------------------------------------------------------------------------------------
