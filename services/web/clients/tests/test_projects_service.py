import requests
import responses
import json
from django.test import SimpleTestCase, override_settings

from clients.projects_service import (
    ProjectsServiceError,
    ProjectsServiceUnavailable,
    create_project,
    get_project,
    get_projects,
    update_project,
)


class ProjectsClientTests(SimpleTestCase):
    """Test Projects service client.

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
    # Test cases for get_projects
    # -----------------------------------------------------------------------------------------------------------------

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
    def test_get_projects_raises_error_when_results_key_is_missing(self):
        """Test get_projects raises error when results key is missing."""
        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            json={"unexpected": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_projects(user_id=123)

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_raises_error_on_upstream_error_status(self):
        """Test get_projects raises error when upstream returns an error status."""
        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            json={"message": "Missing X-User-ID header"},
            status=400,
        )

        with self.assertRaises(ProjectsServiceError):
            get_projects(user_id=123)

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_projects_raises_error_when_results_is_not_a_list(self):
        """Test get_projects raises error when results is not a list."""
        responses.add(
            method=responses.GET,
            url="http://projects:5000/api/projects",
            json={"results": {"id": 1}},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_projects(user_id=123)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_project
    # -----------------------------------------------------------------------------------------------------------------

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_sends_user_id_header_and_returns_project(self):
        """Test get_project calls upstream with user header and returns one project."""
        user_id = 123
        project_id = 1

        payload = {
            "results": [
                {"id": project_id, "name": "Project A", "description": "Test"},
            ],
        }

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            json=payload,
            status=200,
        )

        result = get_project(project_id=project_id, user_id=user_id)

        self.assertEqual(result, payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_unavailable_on_request_exception(self):
        """Test get_project raises ProjectsServiceUnavailable on network failure."""
        user_id = 123
        project_id = 1

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            callback=raise_error,
        )

        with self.assertRaises(ProjectsServiceUnavailable):
            get_project(project_id=project_id, user_id=user_id)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_error_on_upstream_error_status(self):
        """Test get_project raises error when upstream returns an error status."""
        project_id = 1

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"message": "Project not found"},
            status=404,
        )

        with self.assertRaises(ProjectsServiceError):
            get_project(project_id=project_id, user_id=123)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_error_on_invalid_json(self):
        """Test get_project raises error when response JSON is invalid."""
        project_id = 1

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            body="not-json",
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_project(project_id=project_id, user_id=123)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_error_when_results_missing(self):
        """Test get_project raises error when results key is missing."""
        project_id = 1

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"unexpected": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_project(project_id=project_id, user_id=123)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_error_when_results_is_not_a_list(self):
        """Test get_project raises error when results is not a list."""
        project_id = 1

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"results": {"id": project_id}},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_project(project_id=project_id, user_id=123)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_get_project_raises_error_when_results_does_not_contain_one_project(self):
        """Test get_project raises error when results does not contain exactly one project."""
        project_id = 1

        responses.add(
            method=responses.GET,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"results": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            get_project(project_id=project_id, user_id=123)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for create_project
    # -----------------------------------------------------------------------------------------------------------------

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_sends_user_id_header_payload_and_returns_project(self):
        """Test create_project calls upstream with user header, payload, and returns one project."""
        user_id = 123

        request_payload = {
            "name": "Project A",
            "description": "Test",
        }

        response_payload = {
            "results": [
                {"id": 1, "name": "Project A", "description": "Test"},
            ],
        }

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            json=response_payload,
            status=201,
        )

        result = create_project(user_id=user_id, payload=request_payload)

        self.assertEqual(result, response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(request.body.decode("utf-8"), '{"name": "Project A", "description": "Test"}')


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_unavailable_on_request_exception(self):
        """Test create_project raises ProjectsServiceUnavailable on network failure."""
        user_id = 123
        request_payload = {"name": "Project A", "description": "Test"}

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            callback=raise_error,
        )

        with self.assertRaises(ProjectsServiceUnavailable):
            create_project(user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_error_on_upstream_error_status(self):
        """Test create_project raises error when upstream returns an error status."""
        request_payload = {"name": "", "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            json={"message": "Validation error"},
            status=400,
        )

        with self.assertRaises(ProjectsServiceError):
            create_project(user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_error_on_invalid_json(self):
        """Test create_project raises error when response JSON is invalid."""
        request_payload = {"name": "Project A", "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            body="not-json",
            status=201,
        )

        with self.assertRaises(ProjectsServiceError):
            create_project(user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_error_when_results_missing(self):
        """Test create_project raises error when results key is missing."""
        request_payload = {"name": "Project A", "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            json={"unexpected": []},
            status=201,
        )

        with self.assertRaises(ProjectsServiceError):
            create_project(user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_error_when_results_is_not_a_list(self):
        """Test create_project raises error when results is not a list."""
        request_payload = {"name": "Project A", "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            json={"results": {"id": 1}},
            status=201,
        )

        with self.assertRaises(ProjectsServiceError):
            create_project(user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_create_project_raises_error_when_results_does_not_contain_one_project(self):
        """Test create_project raises error when results does not contain exactly one project."""
        request_payload = {"name": "Project A", "description": "Test"}

        responses.add(
            method=responses.POST,
            url="http://projects:5000/api/projects",
            json={"results": []},
            status=201,
        )

        with self.assertRaises(ProjectsServiceError):
            create_project(user_id=123, payload=request_payload)

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for update_project
    # -----------------------------------------------------------------------------------------------------------------

    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_sends_user_id_header_payload_and_returns_project(self):
        """Test update_project calls upstream with user header, payload, and returns one project."""
        user_id = 123
        project_id = 1

        request_payload = {
            "name": "Updated Project",
            "description": "Updated description",
        }

        response_payload = {
            "results": [
                {"id": project_id, "name": "Updated Project", "description": "Updated description"},
            ],
        }

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            json=response_payload,
            status=200,
        )

        result = update_project(project_id=project_id, user_id=user_id, payload=request_payload)

        self.assertEqual(result, response_payload["results"][0])
        self.assertEqual(len(responses.calls), 1)

        request = responses.calls[0].request
        sent_payload = json.loads(request.body.decode("utf-8"))

        self.assertEqual(request.headers.get("X-User-ID"), str(user_id))
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(sent_payload, request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_unavailable_on_request_exception(self):
        """Test update_project raises ProjectsServiceUnavailable on network failure."""
        user_id = 123
        project_id = 1
        request_payload = {"name": "Updated Project"}

        def raise_error(request):
            raise requests.ConnectionError("Service down")

        responses.add_callback(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            callback=raise_error,
        )

        with self.assertRaises(ProjectsServiceUnavailable):
            update_project(project_id=project_id, user_id=user_id, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_error_on_upstream_error_status(self):
        """Test update_project raises error when upstream returns an error status."""
        project_id = 1
        request_payload = {"name": "Updated Project"}

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"message": "Project not found"},
            status=404,
        )

        with self.assertRaises(ProjectsServiceError):
            update_project(project_id=project_id, user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_error_on_invalid_json(self):
        """Test update_project raises error when response JSON is invalid."""
        project_id = 1
        request_payload = {"name": "Updated Project"}

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            body="not-json",
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            update_project(project_id=project_id, user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_error_when_results_missing(self):
        """Test update_project raises error when results key is missing."""
        project_id = 1
        request_payload = {"name": "Updated Project"}

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"unexpected": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            update_project(project_id=project_id, user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_error_when_results_is_not_a_list(self):
        """Test update_project raises error when results is not a list."""
        project_id = 1
        request_payload = {"name": "Updated Project"}

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"results": {"id": project_id}},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            update_project(project_id=project_id, user_id=123, payload=request_payload)


    @responses.activate
    @override_settings(PROJECTS_SERVICE_URL="http://projects:5000")
    def test_update_project_raises_error_when_results_does_not_contain_one_project(self):
        """Test update_project raises error when results does not contain exactly one project."""
        project_id = 1
        request_payload = {"name": "Updated Project"}

        responses.add(
            method=responses.PATCH,
            url=f"http://projects:5000/api/projects/{project_id}",
            json={"results": []},
            status=200,
        )

        with self.assertRaises(ProjectsServiceError):
            update_project(project_id=project_id, user_id=123, payload=request_payload)