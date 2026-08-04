from unittest.mock import patch

from clients.projects_service_client import (
    ProjectsServiceError,
    ProjectsServiceUnavailable,
)
from clients.time_tracking_service_client import (
    TimeTrackingServiceError,
    TimeTrackingServiceUnavailable,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from services.web.app.views import sessions_view


class ProjectsViewTests(TestCase):
    """Test projects page view logic."""

    def setUp(self):
        """Create and authenticate a test user."""
        User = get_user_model()

        self.email = "testuser@example.com"
        self.password = "testpass123"

        self.user = User.objects.create_user(  # type: ignore
            email=self.email,
            password=self.password,
        )

        self.client.login(
            email=self.email,
            password=self.password,
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for projects_view GET
    # -----------------------------------------------------------------------------------------------------------------
    @patch.object(sessions_view.projects_service_client, "get_projects")
    def test_projects_view_loads_projects(self, mock_get_projects):
        """Test projects page loads projects for authenticated user."""
        projects = [
            {"id": 1, "name": "Project A"},
            {"id": 2, "name": "Project B"},
        ]

        mock_get_projects.return_value = projects

        response = self.client.get(reverse("app:projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/projects.html")
        self.assertEqual(response.context["projects"], projects)
        self.assertIsNone(response.context["projects_error"])

        mock_get_projects.assert_called_once_with(self.user.id)

    @patch.object(sessions_view.projects_service_client, "get_projects")
    def test_projects_view_shows_error_when_projects_service_unavailable(self, mock_get_projects):
        """Test projects page shows error when projects service is unavailable."""
        mock_get_projects.side_effect = ProjectsServiceUnavailable

        response = self.client.get(reverse("app:projects"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["projects"], [])
        self.assertEqual(
            response.context["projects_error"],
            "Projects service is currently unavailable.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    def test_projects_view_shows_error_when_projects_service_fails(self, mock_get_projects):
        """Test projects page shows error when projects service fails."""
        mock_get_projects.side_effect = ProjectsServiceError

        response = self.client.get(reverse("app:projects"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["projects"], [])
        self.assertEqual(
            response.context["projects_error"],
            "Could not load projects.",
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for create project
    # -----------------------------------------------------------------------------------------------------------------

    @patch.object(sessions_view.projects_service_client, "create_project")
    def test_projects_view_creates_project_and_redirects(self, mock_create_project):
        """Test valid create project POST creates project and redirects."""
        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "create_project",
                "name": "Project A",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:projects"))

        mock_create_project.assert_called_once_with(
            self.user.id,
            {"name": "Project A"},
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "create_project")
    def test_projects_view_shows_create_error_when_projects_service_unavailable(
        self,
        mock_create_project,
        mock_get_projects,
    ):
        """Test create project shows error when projects service is unavailable."""
        mock_create_project.side_effect = ProjectsServiceUnavailable
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "create_project",
                "name": "Project A",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["project_create_error"],
            "Projects service is currently unavailable.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "create_project")
    def test_projects_view_shows_create_error_when_projects_service_fails(
        self,
        mock_create_project,
        mock_get_projects,
    ):
        """Test create project shows error when projects service fails."""
        mock_create_project.side_effect = ProjectsServiceError
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "create_project",
                "name": "Project A",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["project_create_error"],
            "Could not create project.",
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for update project
    # -----------------------------------------------------------------------------------------------------------------

    @patch.object(sessions_view.projects_service_client, "update_project")
    def test_projects_view_updates_project_and_redirects(self, mock_update_project):
        """Test valid update project POST updates project and redirects."""
        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "update_project",
                "project_id": 1,
                "name": "Updated Project",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:projects"))

        mock_update_project.assert_called_once_with(
            1,
            self.user.id,
            {"name": "Updated Project"},
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "update_project")
    def test_projects_view_shows_update_error_when_projects_service_unavailable(
        self,
        mock_update_project,
        mock_get_projects,
    ):
        """Test update project shows error when projects service is unavailable."""
        mock_update_project.side_effect = ProjectsServiceUnavailable
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "update_project",
                "project_id": 1,
                "name": "Updated Project",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["project_update_error"],
            "Projects service is currently unavailable.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "update_project")
    def test_projects_view_shows_update_error_when_projects_service_fails(
        self,
        mock_update_project,
        mock_get_projects,
    ):
        """Test update project shows error when projects service fails."""
        mock_update_project.side_effect = ProjectsServiceError
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "update_project",
                "project_id": 1,
                "name": "Updated Project",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["project_update_error"],
            "Could not update project.",
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for delete project
    # -----------------------------------------------------------------------------------------------------------------

    @patch.object(sessions_view.projects_service_client, "delete_project")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_deletes_project_and_redirects(
        self,
        mock_get_time_entries,
        mock_delete_project,
    ):
        """Test delete project removes project when no time logs exist."""
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:projects"))

        mock_get_time_entries.assert_called_once_with(
            self.user.id,
            project_id=1,
        )

        mock_delete_project.assert_called_once_with(
            1,
            self.user.id,
        )

    @patch.object(sessions_view.projects_service_client, "delete_project")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_clears_selected_project_session_when_deleted(
        self,
        mock_get_time_entries,
        mock_delete_project,
    ):
        """Test selected project session value is cleared when selected project is deleted."""
        session = self.client.session
        session["selected_project_id"] = 1
        session.save()

        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("selected_project_id", self.client.session)

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "delete_project")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_does_not_delete_project_when_time_logs_exist(
        self,
        mock_get_time_entries,
        mock_delete_project,
        mock_get_projects,
    ):
        """Test delete project is blocked when project has time logs."""
        mock_get_time_entries.return_value = [
            {"id": 1, "project_id": 1},
        ]

        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_delete_id"], 1)

        self.assertEqual(
            response.context["project_delete_error"],
            "Cannot delete this project because it has time logs.",
        )

        mock_delete_project.assert_not_called()

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_shows_delete_error_when_time_tracking_service_unavailable(
        self,
        mock_get_time_entries,
        mock_get_projects,
    ):
        """Test delete project shows error when time tracking service is unavailable."""
        mock_get_time_entries.side_effect = TimeTrackingServiceUnavailable
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_delete_id"], 1)

        self.assertEqual(
            response.context["project_delete_error"],
            "Time tracking service is currently unavailable.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_shows_delete_error_when_time_tracking_service_fails(
        self,
        mock_get_time_entries,
        mock_get_projects,
    ):
        """Test delete project shows error when checking time logs fails."""
        mock_get_time_entries.side_effect = TimeTrackingServiceError
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_delete_id"], 1)

        self.assertEqual(
            response.context["project_delete_error"],
            "Could not check whether this project has time logs.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "delete_project")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_shows_delete_error_when_projects_service_unavailable(
        self,
        mock_get_time_entries,
        mock_delete_project,
        mock_get_projects,
    ):
        """Test delete project shows error when projects service is unavailable."""
        mock_get_time_entries.return_value = []
        mock_delete_project.side_effect = ProjectsServiceUnavailable
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_delete_id"], 1)

        self.assertEqual(
            response.context["project_delete_error"],
            "Projects service is currently unavailable.",
        )

    @patch.object(sessions_view.projects_service_client, "get_projects")
    @patch.object(sessions_view.projects_service_client, "delete_project")
    @patch.object(sessions_view.time_tracking_service_client, "get_time_entries")
    def test_projects_view_shows_delete_error_when_projects_service_fails(
        self, mock_get_time_entries, mock_delete_project, mock_get_projects
    ):
        """Test delete project shows error when project deletion fails."""
        mock_get_time_entries.return_value = []
        mock_delete_project.side_effect = ProjectsServiceError
        mock_get_projects.return_value = []

        response = self.client.post(
            reverse("app:projects"),
            {
                "form_type": "delete_project",
                "project_id": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_delete_id"], 1)

        self.assertEqual(
            response.context["project_delete_error"],
            "Could not delete project.",
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for authentication
    # -----------------------------------------------------------------------------------------------------------------

    def test_projects_view_requires_login(self):
        """Test projects page redirects anonymous users to login."""
        self.client.logout()

        response = self.client.get(reverse("app:projects"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
