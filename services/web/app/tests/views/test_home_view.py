from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    """Test Home page view logic."""

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

    def test_home_view_returns_success_response(self):
        """Test home view renders successfully."""
        response = self.client.get(reverse("app:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/home.html")
