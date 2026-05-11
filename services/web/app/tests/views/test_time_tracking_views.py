# tests/test_time_tracking_views.py

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from app.views.time_tracking_views import clock_in_view, clock_out_view
from clients.time_tracking_service import TimeTrackingServiceError


class ClockInViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email="clockin@example.com",
            password="password",
        )

    @patch("app.views.time_tracking_views.create_time_entry")
    def test_clock_in_creates_time_entry_and_redirects(self, mock_create_time_entry):
        request = self.factory.get("/clock-in/")
        request.user = self.user
        request.session = {"selected_project_id": 123}

        response = clock_in_view(request)

        mock_create_time_entry.assert_called_once_with(self.user.id, {"project_id": 123})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))

    @patch("app.views.time_tracking_views.create_time_entry")
    def test_clock_in_redirects_when_no_project_selected(self, mock_create_time_entry):
        request = self.factory.get("/clock-in/")
        request.user = self.user
        request.session = {}

        response = clock_in_view(request)

        mock_create_time_entry.assert_not_called()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))

    @patch("app.views.time_tracking_views.create_time_entry")
    def test_clock_in_handles_service_error(self, mock_create_time_entry):
        mock_create_time_entry.side_effect = TimeTrackingServiceError()

        request = self.factory.get("/clock-in/")
        request.user = self.user
        request.session = {"selected_project_id": 123}

        response = clock_in_view(request)

        mock_create_time_entry.assert_called_once()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))


class ClockOutViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(email="clockout@example.com", password="password")

    @patch("app.views.time_tracking_views.stop_time_entry")
    @patch("app.views.time_tracking_views.get_time_entries")
    def test_clock_out_stops_running_entry(self, mock_get_time_entries, mock_stop_time_entry):
        mock_get_time_entries.return_value = [{"id": "entry-123"}]

        request = self.factory.get("/clock-out/")
        request.user = self.user
        request.session = {"selected_project_id": 123}

        response = clock_out_view(request)

        mock_get_time_entries.assert_called_once_with(self.user.id, project_id=123, running_only=True)
        mock_stop_time_entry.assert_called_once_with(self.user.id, "entry-123")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))


    @patch("app.views.time_tracking_views.stop_time_entry")
    @patch("app.views.time_tracking_views.get_time_entries")
    def test_clock_out_does_nothing_when_no_running_entries(self, mock_get_time_entries, mock_stop_time_entry):
        mock_get_time_entries.return_value = []

        request = self.factory.get("/clock-out/")
        request.user = self.user
        request.session = {"selected_project_id": 123}

        response = clock_out_view(request)

        mock_stop_time_entry.assert_not_called()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("app:dashboard"))
