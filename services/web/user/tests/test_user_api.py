from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicAuthTests(TestCase):
    """Test public (unauthenticated) auth views."""

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """Test register page loads successfully."""
        res = self.client.get(reverse("register"))
        self.assertEqual(res.status_code, 200)

    def test_register_user_success(self):
        """Test user can register successfully."""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        res = self.client.post(reverse("register"), payload)

        self.assertEqual(res.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email=payload["email"]).exists())

    def test_register_password_mismatch(self):
        """Test error if passwords do not match."""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpass123",
            "password_confirm": "wrongpass",
        }

        res = self.client.post(reverse("register"), payload)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Passwords do not match")

    def test_login_page_loads(self):
        """Test login page loads successfully."""
        res = self.client.get(reverse("login"))
        self.assertEqual(res.status_code, 200)

    def test_login_success(self):
        """Test user can log in and is redirected."""
        create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
        )

        res = self.client.post(
            reverse("login"),
            {
                "email": "test@example.com",
                "password": "testpass123",
            },
        )

        self.assertRedirects(res, reverse("dashboard"))

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
        )

        res = self.client.post(
            reverse("login"),
            {
                "email": "test@example.com",
                "password": "wrongpass",
            },
        )

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Invalid email or password")


class PrivateAuthTests(TestCase):
    """Test authenticated views."""

    def setUp(self):
        self.client = Client()
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
        )
        self.client.login(email="test@example.com", password="testpass123")

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication."""
        self.client.logout()
        res = self.client.get(reverse("dashboard"))

        self.assertRedirects(res, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_access(self):
        """Test logged in user can access dashboard."""
        res = self.client.get(reverse("dashboard"))
        self.assertEqual(res.status_code, 200)

    def test_logout(self):
        """Test user can log out."""
        res = self.client.post(reverse("logout"))
        self.assertRedirects(res, reverse("login"))

        res = self.client.get(reverse("dashboard"))
        self.assertRedirects(res, f"{reverse('login')}?next={reverse('dashboard')}")
