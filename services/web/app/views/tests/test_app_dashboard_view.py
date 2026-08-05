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

from app.views import dashboard_view


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(  # type: ignore
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.login(email="testuser@example.com", password="testpass123")

    @staticmethod
    def _running_session(project_id: int = 1) -> dict:
        return {
            "id": 10,
            "project_id": project_id,
            "started_at": "2026-08-05T09:00:00+00:00",
            "ended_at": None,
            "duration_seconds": 3660,
        }

    @staticmethod
    def _finished_session(project_id: int = 1) -> dict:
        return {
            "id": 9,
            "project_id": project_id,
            "started_at": "2026-08-04T09:00:00+00:00",
            "ended_at": "2026-08-04T10:30:00+00:00",
            "duration_seconds": 5400,
        }

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    def test_first_load_defaults_projects_dropdown_to_active_project(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_get_projects.return_value = [
            {"id": 1, "name": "Project A"},
            {"id": 2, "name": "Project B"},
        ]
        mock_get_time_entries.return_value = [self._running_session(project_id=1)]

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["active_project"]["id"], 1)
        self.assertEqual(response.context["selected_project"]["id"], 1)
        self.assertEqual(self.client.session["selected_project_id"], 1)
        self.assertTrue(response.context["has_running_session"])

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    def test_projects_dropdown_is_independent_of_active_project(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_get_projects.return_value = [
            {"id": 1, "name": "Project A"},
            {"id": 2, "name": "Project B"},
        ]
        mock_get_time_entries.return_value = [self._running_session(project_id=1)]

        session = self.client.session
        session["selected_project_id"] = 2
        session.save()

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["active_project"]["id"], 1)
        self.assertEqual(response.context["selected_project"]["id"], 2)

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    def test_last_session_supplies_active_card_when_not_clocked_in(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_get_projects.return_value = [{"id": 2, "name": "Project B"}]
        mock_get_time_entries.return_value = [self._finished_session(project_id=2)]

        response = self.client.get(reverse("app:dashboard"))

        self.assertIsNone(response.context["active_session"])
        self.assertEqual(response.context["active_project"]["id"], 2)
        self.assertEqual(response.context["selected_project"]["id"], 2)

    def test_select_project_changes_only_projects_card_session_state(self):
        response = self.client.post(
            reverse("app:dashboard"),
            {"form_type": "select_project", "project_id": "2"},
        )

        self.assertRedirects(response, reverse("app:dashboard"))
        self.assertEqual(self.client.session["selected_project_id"], 2)

    @patch.object(dashboard_view.time_tracking_service_client, "create_time_entry")
    @patch.object(dashboard_view.time_tracking_service_client, "stop_time_entry")
    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    def test_switch_project_stops_current_entry_and_starts_new_one(
        self,
        mock_get_time_entries,
        mock_stop_time_entry,
        mock_create_time_entry,
    ):
        mock_get_time_entries.return_value = [{"id": 99}]

        response = self.client.post(
            reverse("app:dashboard"),
            {"form_type": "switch_project", "project_id": "2"},
        )

        self.assertRedirects(response, reverse("app:dashboard"))
        mock_get_time_entries.assert_called_once_with(self.user.id, running_only=True)
        mock_stop_time_entry.assert_called_once_with(self.user.id, 99)
        mock_create_time_entry.assert_called_once_with(
            self.user.id,
            {"project_id": 2},
        )
        self.assertEqual(self.client.session["selected_project_id"], 2)

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    @patch.object(dashboard_view.time_tracking_service_client, "create_time_entry")
    def test_switch_project_error_is_rendered(
        self,
        mock_create_time_entry,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_create_time_entry.side_effect = TimeTrackingServiceError
        mock_get_projects.return_value = [{"id": 1, "name": "Project A"}]
        mock_get_time_entries.return_value = []

        response = self.client.post(
            reverse("app:dashboard"),
            {"form_type": "switch_project", "project_id": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["switch_project_error"], "Could not switch project.")

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    def test_service_errors_are_added_to_context(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_get_projects.side_effect = ProjectsServiceUnavailable
        mock_get_time_entries.side_effect = TimeTrackingServiceUnavailable

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["projects"], [])
        self.assertEqual(
            response.context["projects_error"],
            "Projects service is currently unavailable.",
        )
        self.assertEqual(
            response.context["sessions_error"],
            "Time tracking service is currently unavailable.",
        )

    @patch.object(dashboard_view.time_tracking_service_client, "get_time_entries")
    @patch.object(dashboard_view.projects_service_client, "get_projects")
    def test_generic_service_errors_are_added_to_context(
        self,
        mock_get_projects,
        mock_get_time_entries,
    ):
        mock_get_projects.side_effect = ProjectsServiceError
        mock_get_time_entries.side_effect = TimeTrackingServiceError

        response = self.client.get(reverse("app:dashboard"))

        self.assertEqual(response.context["projects_error"], "Could not load projects.")
        self.assertEqual(response.context["sessions_error"], "Could not load sessions.")

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("app:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
