from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clients.projects_service import ProjectsServiceError, ProjectsServiceUnavailable
from clients.time_tracking_service import TimeTrackingServiceError, TimeTrackingServiceUnavailable


class DashboardViewTests(TestCase):
    """Test dashboard page view logic."""

    def setUp(self):
        """Create and authenticate a test user."""
        User = get_user_model()

        self.email = "testuser@example.com"
        self.password = "testpass123"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
        )

        self.client.login(
            email=self.email,
            password=self.password,
        )

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_loads_projects_and_sessions(self, mock_get_projects, mock_get_time_entries):
        """Test dashboard loads projects and sessions."""
        mock_get_projects.return_value = [{"id": 1, "name": "Project A"}]
        mock_get_time_entries.return_value = [
            {
                "id": 10,
                "project_id": 1,
                "created_at": "2025-01-01T09:00:00",
                "ended_at": "2025-01-01T10:30:00",
                "duration_seconds": 5400,
            },
        ]

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/dashboard.html")
        self.assertEqual(response.context["projects"], [{"id": 1, "name": "Project A"}])
        self.assertEqual(response.context["sessions"][0]["project_name"], "Project A")
        self.assertEqual(response.context["sessions"][0]["duration_display"], "1h 30m")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_uses_fallback_project_name(self, mock_get_projects, mock_get_time_entries):
        """Test dashboard uses fallback project name when project is missing."""
        mock_get_projects.return_value = []
        mock_get_time_entries.return_value = [
            {
                "id": 10,
                "project_id": 99,
                "created_at": "2025-01-01T09:00:00",
                "ended_at": None,
                "duration_seconds": None,
            },
        ]

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["sessions"][0]["project_name"], "Project 99")
        self.assertEqual(response.context["sessions"][0]["ended_at_display"], "Running")
        self.assertEqual(response.context["sessions"][0]["duration_display"], "-")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_sets_running_session_context(self, mock_get_projects, mock_get_time_entries):
        """Test dashboard detects running session and formats running duration."""
        mock_get_projects.return_value = [{"id": 1, "name": "Project A"}]
        mock_get_time_entries.return_value = [
            {
                "id": 10,
                "project_id": 1,
                "created_at": "2025-01-01T09:00:00",
                "ended_at": None,
                "duration_seconds": 3660,
            },
        ]

        response = self.client.get(reverse("app:dashboard"))

        self.assertTrue(response.context["has_running_session"])
        self.assertEqual(response.context["running_duration_display"], "1h 1 mins")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_shows_projects_error_when_service_unavailable(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test dashboard shows projects unavailable error."""
        mock_get_projects.side_effect = ProjectsServiceUnavailable
        mock_get_time_entries.return_value = []

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["projects"], [])
        self.assertEqual(response.context["projects_error"], "Projects service is currently unavailable.")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_shows_projects_error_when_service_fails(self, mock_get_projects, mock_get_time_entries):
        """Test dashboard shows projects service error."""
        mock_get_projects.side_effect = ProjectsServiceError
        mock_get_time_entries.return_value = []

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["projects"], [])
        self.assertEqual(response.context["projects_error"], "Could not load projects.")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_shows_sessions_error_when_service_unavailable(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test dashboard shows sessions unavailable error."""
        mock_get_projects.return_value = []
        mock_get_time_entries.side_effect = TimeTrackingServiceUnavailable

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["sessions"], [])
        self.assertEqual(response.context["sessions_error"], "Time tracking service is currently unavailable.")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    def test_dashboard_view_shows_sessions_error_when_service_fails(self, mock_get_projects, mock_get_time_entries):
        """Test dashboard shows sessions service error."""
        mock_get_projects.return_value = []
        mock_get_time_entries.side_effect = TimeTrackingServiceError

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["sessions"], [])
        self.assertEqual(response.context["sessions_error"], "Could not load sessions.")

    def test_dashboard_view_selects_project_and_redirects(self):
        """Test selected project POST stores project ID in session."""
        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "select_project",
                "project_id": "1",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))
        self.assertEqual(self.client.session["selected_project_id"], 1)

    def test_dashboard_view_clears_selected_project_and_redirects(self):
        """Test selected project POST clears project ID when empty."""
        session = self.client.session
        session["selected_project_id"] = 1
        session.save()

        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "select_project",
                "project_id": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("selected_project_id", self.client.session)

    @patch("app.views.dashboard_view.update_time_entry")
    def test_dashboard_view_updates_session_and_redirects(self, mock_update_time_entry):
        """Test update session POST updates time entry."""
        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "update_session",
                "session_id": "10",
                "started_at": "2025-01-01T09:00",
                "ended_at": "2025-01-01T10:00",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))

        mock_update_time_entry.assert_called_once_with(
            self.user.id,
            10,
            {
                "started_at": "2025-01-01T09:00",
                "ended_at": "2025-01-01T10:00",
            },
        )

    @patch("app.views.dashboard_view.update_time_entry")
    def test_dashboard_view_updates_session_with_empty_ended_at(self, mock_update_time_entry):
        """Test update session POST converts empty ended_at to None."""
        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "update_session",
                "session_id": "10",
                "started_at": "2025-01-01T09:00",
                "ended_at": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        mock_update_time_entry.assert_called_once_with(
            self.user.id,
            10,
            {
                "started_at": "2025-01-01T09:00",
                "ended_at": None,
            },
        )

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    @patch("app.views.dashboard_view.update_time_entry")
    def test_dashboard_view_shows_update_error_when_service_unavailable(
        self,
        mock_update_time_entry,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test update session shows unavailable error."""
        mock_update_time_entry.side_effect = TimeTrackingServiceUnavailable
        mock_get_projects.return_value = []
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "update_session",
                "session_id": "10",
                "started_at": "2025-01-01T09:00",
                "ended_at": "",
            },
        )

        self.assertEqual(response.context["session_update_error"], "Time tracking service is currently unavailable.")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    @patch("app.views.dashboard_view.update_time_entry")
    def test_dashboard_view_shows_update_error_when_service_fails(
        self,
        mock_update_time_entry,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test update session shows service error."""
        mock_update_time_entry.side_effect = TimeTrackingServiceError
        mock_get_projects.return_value = []
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "update_session",
                "session_id": "10",
                "started_at": "2025-01-01T09:00",
                "ended_at": "",
            },
        )

        self.assertEqual(response.context["session_update_error"], "Could not update session.")

    @patch("app.views.dashboard_view.delete_time_entry")
    def test_dashboard_view_deletes_session_and_redirects(self, mock_delete_time_entry):
        """Test delete session POST deletes time entry."""
        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "delete_session",
                "session_id": "10",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))
        mock_delete_time_entry.assert_called_once_with(self.user.id, 10)

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    @patch("app.views.dashboard_view.delete_time_entry")
    def test_dashboard_view_shows_delete_error_when_service_unavailable(
        self,
        mock_delete_time_entry,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test delete session shows unavailable error."""
        mock_delete_time_entry.side_effect = TimeTrackingServiceUnavailable
        mock_get_projects.return_value = []
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "delete_session",
                "session_id": "10",
            },
        )

        self.assertEqual(response.context["session_delete_error"], "Time tracking service is currently unavailable.")

    @patch("app.views.dashboard_view.get_time_entries")
    @patch("app.views.dashboard_view.get_projects")
    @patch("app.views.dashboard_view.delete_time_entry")
    def test_dashboard_view_shows_delete_error_when_service_fails(
        self,
        mock_delete_time_entry,
        mock_get_projects,
        mock_get_time_entries,
    ):
        """Test delete session shows service error."""
        mock_delete_time_entry.side_effect = TimeTrackingServiceError
        mock_get_projects.return_value = []
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:dashboard"),
            {
                "form_type": "delete_session",
                "session_id": "10",
            },
        )

        self.assertEqual(response.context["session_delete_error"], "Could not delete session.")

    def test_dashboard_view_requires_login(self):
        """Test dashboard redirects anonymous users to login."""
        self.client.logout()

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
