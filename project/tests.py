from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import PasswordResetOTP

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

    def test_register_duplicate_username(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "new@example.com",
                "password": "Test@12345",
                "confirm_password": "Test@12345",
                "mobile_number": "9999999999",
                "other_mobile_number": "",
                "date_birth": "2000-01-01",
                "address": "Surat",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_register_duplicate_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "anotheruser",
                "email": "test@example.com",
                "password": "Test@12345",
                "confirm_password": "Test@12345",
                "mobile_number": "9999999999",
                "other_mobile_number": "",
                "date_birth": "2000-01-01",
                "address": "Surat",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "Test@123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "WrongPassword",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_login_invalid_username(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "wronguser",
                "password": "Test@123",
            },
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

    def test_profile_update_requires_login(self):
        response = self.client.post(reverse("profile"), {"address": "Rajkot"})

        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        self.client.login(username="testuser", password="Test@123")

        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg",
        )

        response = self.client.post(
            reverse("profile"),
            {
                "mobile_number": "9999999999",
                "other_mobile_number": "",
                "date_birth": "2000-01-01",
                "address": "Rajkot",
                "profile_image": image,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.mobile_number, "9999999999")
        self.assertEqual(self.user.address, "Rajkot")

    def test_contact_invalid_registered_email(self):
        self.client.login(username="testuser", password="Test@123")

        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test",
                "email": "wrong@example.com",
                "message": "Hello",
            },
        )

        self.assertEqual(response.status_code, 200)

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

        otp = PasswordResetOTP.objects.filter(email="test@example.com").first()

        self.assertIsNotNone(otp)
        self.assertEqual(otp.email, "test@example.com")
        self.assertEqual(len(otp.otp), 6)
        self.assertIsNotNone(otp.expiry)

    def test_send_otp_invalid_email(self):
        response = self.client.post(
            reverse("forgot_password"),
            {"send_otp": "1", "email": "invalid@example.com"},
        )

        self.assertEqual(response.status_code, 200)

    def test_verify_otp(self):
        PasswordResetOTP.objects.create(
            email="test@example.com",
            otp="123456",
            expiry=timezone.now() + timedelta(seconds=30),
        )

        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"),
            {
                "verify_otp": "1",
                "otp": "123456",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_verify_invalid_otp(self):
        PasswordResetOTP.objects.create(
            email="test@example.com",
            otp="123456",
            expiry=timezone.now() + timedelta(seconds=30),
        )

        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"), {"verify_otp": "1", "otp": "654321"}
        )

        self.assertEqual(response.status_code, 200)

    def test_verify_expired_otp(self):
        PasswordResetOTP.objects.create(
            email="test@example.com",
            otp="123456",
            expiry=timezone.now() - timedelta(seconds=1),
        )

        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"), {"verify_otp": "1", "otp": "123456"}
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        PasswordResetOTP.objects.create(
            email="test@example.com",
            otp="123456",
            expiry=timezone.now() + timedelta(seconds=30),
        )

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
        self.assertFalse(
            PasswordResetOTP.objects.filter(email="test@example.com").exists()
        )

    def test_reset_password_mismatch(self):
        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"),
            {
                "reset_password": "1",
                "new_password": "NewPass@123",
                "confirm_password": "WrongPass@123",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_password_invalid_format(self):
        session = self.client.session
        session["reset_email"] = "test@example.com"
        session.save()

        response = self.client.post(
            reverse("forgot_password"),
            {
                "reset_password": "1",
                "new_password": "123",
                "confirm_password": "123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Test@123"))
