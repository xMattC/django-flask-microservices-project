# user/tests/test_register_form.py

from django.contrib.auth import get_user_model
from django.test import TestCase

from user.forms import RegisterForm


class RegisterFormTests(TestCase):
    def test_valid_form(self):
        form = RegisterForm(
            data={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        self.assertTrue(form.is_valid())

    def test_passwords_must_match(self):
        form = RegisterForm(
            data={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "password_confirm": "differentpassword",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_save_hashes_password(self):
        form = RegisterForm(
            data={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))

    def test_save_creates_user(self):
        form = RegisterForm(
            data={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(
            get_user_model().objects.count(),
            1,
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
