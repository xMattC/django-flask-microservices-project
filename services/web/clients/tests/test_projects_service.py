import requests
import responses
from django.test import SimpleTestCase, override_settings

from clients.projects_service import get_projects, ProjectsServiceUnavailable, ProjectsServiceError


class ProjectsClientTests(SimpleTestCase):
    """Test Projects service client."""

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_sends_user_id_header_and_returns_results(self):
        """Test get_projects calls upstream with user header and returns results."""
        user_id = 123

        payload = {
            "results": [
                {"id": 1, "name": "Project A", "description": "Test"},
            ],
        }

        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            json=payload,
            status=200,
        )

        result = get_projects(user_id=user_id)

        self.assertEqual(result, payload["results"])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_raises_unavailable_on_request_exception(self):
        """Test get_projects raises ProjectsServiceUnavailable on network failure."""
        user_id = 123

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            callback=raise_error,
        )

        with self.assertRaises(ProjectsServiceUnavailable):
            get_projects(user_id=user_id)

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_raises_error_on_invalid_json(self):
        """Test get_projects raises error when response JSON is invalid."""
        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            body="not-json",
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_projects(user_id=123)

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_raises_error_when_results_missing(self):
        """Test get_projects raises error when results key is missing."""
        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            json={"unexpected": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_projects(user_id=123)
