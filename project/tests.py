from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from project.views import OTP_STORE

User = get_user_model()


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@123",
            mobile_number="9876543210",
            other_mobile_number="9876543211",
            address="Ahmedabad",
        )

    def test_register_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "Test@12345",
                "confirm_password": "Test@12345",
                "mobile_number": "9999999999",
                "other_mobile_number": "",
                "date_birth": "2000-01-01",
                "address": "Surat",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_success(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "Test@123"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "WrongPassword"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_logged_in(self):
        self.client.login(username="testuser", password="Test@123")

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        self.client.login(username="testuser", password="Test@123")

        response = self.client.post(
            reverse("profile"),
            {
                "username": "updateduser",
                "mobile_number": "9999999999",
                "other_mobile_number": "",
                "date_birth": "2000-01-01",
                "address": "Rajkot",
                "current_password": "Test@123",
                "new_password": "",
                "confirm_password": "",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_logout(self):
        self.client.login(username="testuser", password="Test@123")

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_send_otp_valid_email(self):
        response = self.client.post(
            reverse("forgot_password"), {"send_otp": "1", "email": "test@example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("test@example.com", OTP_STORE)

    def test_send_otp_invalid_email(self):
        response = self.client.post(
            reverse("forgot_password"),
            {"send_otp": "1", "email": "invalid@example.com"},
        )

        self.assertEqual(response.status_code, 200)

    def test_verify_otp(self):
        OTP_STORE["test@example.com"] = "123456"

        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"), {"verify_otp": "1", "otp": "123456"}
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        OTP_STORE["test@example.com"] = "123456"

        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"),
            {
                "reset_password": "1",
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass@123"))
