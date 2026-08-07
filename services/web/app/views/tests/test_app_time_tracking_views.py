from unittest.mock import patch

from clients.time_tracking_service_client import TimeTrackingServiceError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from app.views import time_tracking_views


class TimeTrackingViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(  # type: ignore
            email="timer@example.com",
            password="password",
        )
        self.client.login(email="timer@example.com", password="password")

    @patch.object(time_tracking_views.time_tracking_service_client, "create_time_entry")
    def test_clock_in_uses_posted_active_project_id(self, mock_create_time_entry):
        session = self.client.session
        session["selected_project_id"] = 999
        session.save()

        response = self.client.post(
            reverse("app:clock-in"),
            {"project_id": "123"},
        )

        mock_create_time_entry.assert_called_once_with(
            self.user.id,
            {"project_id": 123},
        )
        self.assertRedirects(response, reverse("app:dashboard"))

    @patch.object(time_tracking_views.time_tracking_service_client, "create_time_entry")
    def test_clock_in_does_not_run_without_project_id(self, mock_create_time_entry):
        response = self.client.post(reverse("app:clock-in"), {})

        mock_create_time_entry.assert_not_called()
        self.assertRedirects(response, reverse("app:dashboard"))

    def test_clock_in_rejects_get(self):
        response = self.client.get(reverse("app:clock-in"))
        self.assertEqual(response.status_code, 405)

    @patch.object(time_tracking_views.time_tracking_service_client, "stop_time_entry")
    @patch.object(time_tracking_views.time_tracking_service_client, "get_time_entries")
    def test_clock_out_ignores_projects_dropdown_selection(
        self,
        mock_get_time_entries,
        mock_stop_time_entry,
    ):
        session = self.client.session
        session["selected_project_id"] = 999
        session.save()
        mock_get_time_entries.return_value = [{"id": "entry-123", "project_id": 1}]

        response = self.client.post(reverse("app:clock-out"))

        mock_get_time_entries.assert_called_once_with(
            self.user.id,
            running_only=True,
        )
        mock_stop_time_entry.assert_called_once_with(self.user.id, "entry-123")
        self.assertRedirects(response, reverse("app:dashboard"))

    @patch.object(time_tracking_views.time_tracking_service_client, "stop_time_entry")
    @patch.object(time_tracking_views.time_tracking_service_client, "get_time_entries")
    def test_clock_out_does_nothing_when_no_entry_is_running(
        self,
        mock_get_time_entries,
        mock_stop_time_entry,
    ):
        mock_get_time_entries.return_value = []

        response = self.client.post(reverse("app:clock-out"))

        mock_stop_time_entry.assert_not_called()
        self.assertRedirects(response, reverse("app:dashboard"))

    @patch.object(time_tracking_views.time_tracking_service_client, "get_time_entries")
    def test_clock_out_handles_service_error(self, mock_get_time_entries):
        mock_get_time_entries.side_effect = TimeTrackingServiceError

        response = self.client.post(reverse("app:clock-out"))

        self.assertRedirects(response, reverse("app:dashboard"))

    def test_clock_out_rejects_get(self):
        response = self.client.get(reverse("app:clock-out"))
        self.assertEqual(response.status_code, 405)
