import responses
from django.test import SimpleTestCase, override_settings

from clients.projects_service import get_projects


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