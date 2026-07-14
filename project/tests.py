# Standard library imports
from datetime import timedelta
from io import BytesIO

# Django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Third-party imports
from PIL import Image
from rest_framework.test import APIRequestFactory

# Local application imports
from project.views import ProjectModelViewSet

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common helper methods."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@123",
            mobile_number="9876543210",
            other_mobile_number="9876543211",
            address="Ahmedabad",
        )

    def login_user(self):
        self.client.login(username="testuser", password="Test@123")

    def set_reset_session(self, email="test@example.com"):
        session = self.client.session
        session["reset_email"] = email
        session.save()

    def assert_message(self, response, text):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(text in str(message) for message in messages))

    def set_otp(self, otp="123456", expiry=30):
        self.user.otp = otp
        self.user.otp_expiry = timezone.now() + timedelta(seconds=expiry)
        self.user.save()

    def create_image(self):
        image_io = BytesIO()
        Image.new("RGB", (100, 100), "white").save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test.jpg", image_io.read(), content_type="image/jpeg"
        )

    def get_view(self, request):
        view = ProjectModelViewSet()
        view.request = request
        return view


class AuthenticationViewTests(BaseTestCase):
    """Tests for authentication views."""

    def test_register_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def register_data(self, **kwargs):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Test@12345",
            "confirm_password": "Test@12345",
            "mobile_number": "9999999999",
            "other_mobile_number": "",
            "date_birth": "2000-01-01",
            "address": "Surat",
        }
        data.update(kwargs)
        return data

    def test_register_success(self):
        response = self.client.post(
            reverse("register"),
            self.register_data(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assert_message(response, "User registered successfully.")

    def test_register_duplicate_username(self):
        response = self.client.post(
            reverse("register"),
            self.register_data(username="testuser", email="another@example.com"),
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Username already exists")

    def test_register_duplicate_email(self):
        response = self.client.post(
            reverse("register"),
            self.register_data(username="anotheruser", email="test@example.com"),
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Email already exists")

    def test_register_future_date_birth(self):
        response = self.client.post(
            reverse("register"),
            self.register_data(
                username="futureuser",
                email="future@example.com",
                date_birth="2099-01-01",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Date of birth cannot be in the future.",
        )

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
        self.assert_message(response, "Invalid username or password")

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
        self.login_user()
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.login_user()

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))


class ProfileViewTests(BaseTestCase):
    """Tests for profile view."""

    def profile_data(self, **kwargs):
        data = {
            "mobile_number": "9999999999",
            "other_mobile_number": "",
            "date_birth": "2000-01-01",
            "address": "Rajkot",
        }
        data.update(kwargs)
        return data

    def test_login_authenticated_user(self):
        self.login_user()
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_update_requires_login(self):
        response = self.client.post(
            reverse("profile"),
            self.profile_data(),
        )
        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        self.login_user()

        response = self.client.post(
            reverse("profile"),
            self.profile_data(profile_image=self.create_image()),
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.mobile_number, "9999999999")
        self.assertEqual(self.user.address, "Rajkot")

    def test_profile_invalid_image(self):
        self.login_user()

        invalid_file = SimpleUploadedFile(
            "fake.jpg", b"This is not a real image", content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("profile"),
            self.profile_data(profile_image=invalid_file),
            follow=True,
        )
        print(response.context["form"].errors)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "profile_image",
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
        )

    def test_profile_invalid_image_format(self):
        self.login_user()

        image = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(image, format="GIF")
        image.seek(0)
        gif_file = SimpleUploadedFile(
            "test.gif",
            image.read(),
            content_type="image/gif",
        )
        response = self.client.post(
            reverse("profile"),
            self.profile_data(profile_image=gif_file),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Only JPG and PNG images are allowed.")

    def test_profile_change_password(self):
        self.login_user()

        response = self.client.post(
            reverse("profile"),
            self.profile_data(
                old_password="Test@123",
                new_password="NewPass@123",
                confirm_password="NewPass@123",
            ),
            follow=True,
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("NewPass@123"))
        self.assert_message(response, "Password changed successfully.")

    def test_profile_invalid_old_password(self):
        self.login_user()

        response = self.client.post(
            reverse("profile"),
            self.profile_data(
                old_password="Wrong@123",
                new_password="NewPass@123",
                confirm_password="NewPass@123",
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Old password is incorrect.")

    def test_profile_password_mismatch(self):
        self.login_user()

        response = self.client.post(
            reverse("profile"),
            self.profile_data(
                old_password="Test@123",
                new_password="NewPass@123",
                confirm_password="Another@123",
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(
            response,
            "New password and confirm password do not match.",
        )

    def test_services_page_loads(self):
        response = self.client.get(reverse("services"))
        self.assertEqual(response.status_code, 200)


class ContactViewTests(BaseTestCase):
    """Tests for contact view."""

    def test_contact_invalid_registered_email(self):
        self.login_user()
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test",
                "email": "wrong@example.com",
                "message": "Hello",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Please enter your registered email address.")

    def test_contact_get(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)

    def test_contact_requires_login(self):
        response = self.client.post(
            reverse("contact"),
            {"name": "Test", "email": "test@example.com", "message": "Hello"},
        )

        self.assertRedirects(response, reverse("login"))


class ForgotPasswordViewTests(BaseTestCase):
    """Tests for forgot password flow."""

    def test_send_otp_valid_email(self):
        response = self.client.post(
            reverse("forgot_password"), {"send_otp": "1", "email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp)
        self.assertEqual(len(self.user.otp), 6)
        self.assertIsNotNone(self.user.otp_expiry)

    def test_send_otp_invalid_email(self):
        response = self.client.post(
            reverse("forgot_password"),
            {"send_otp": "1", "email": "invalid@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Invalid email")

    def test_verify_otp(self):
        self.set_otp()
        self.set_reset_session()
        response = self.client.post(
            reverse("forgot_password"),
            {
                "verify_otp": "1",
                "otp": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "OTP verified.")

    def test_verify_invalid_otp(self):
        self.set_otp()
        self.set_reset_session()
        response = self.client.post(
            reverse("forgot_password"), {"verify_otp": "1", "otp": "654321"}
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Invalid OTP")

    def test_verify_expired_otp(self):
        self.set_otp(expiry=-1)
        self.set_reset_session()
        response = self.client.post(
            reverse("forgot_password"), {"verify_otp": "1", "otp": "123456"}
        )
        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "OTP has expired")
        self.user.refresh_from_db()
        self.assertIsNone(self.user.otp)
        self.assertIsNone(self.user.otp_expiry)

    def test_reset_password(self):
        self.set_otp()
        self.set_reset_session()
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
        self.assert_message(response, "Password reset successful.")

    def test_reset_password_mismatch(self):
        self.set_reset_session()
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
        self.set_reset_session()
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

    def test_forgot_password_get(self):
        response = self.client.get(reverse("forgot_password"))
        self.assertEqual(response.status_code, 200)

    def test_resend_otp_session_expired(self):
        response = self.client.post(
            reverse("forgot_password"),
            {"resend_otp": "1"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "Session expired. Please enter email again.")

    def test_resend_otp_success(self):
        self.set_reset_session()

        response = self.client.post(
            reverse("forgot_password"),
            {"resend_otp": "1"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp)
        self.assert_message(response, "OTP resent successfully.")

    def test_verify_otp_not_found(self):
        self.set_reset_session()

        response = self.client.post(
            reverse("forgot_password"),
            {"verify_otp": "1", "otp": "123456"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assert_message(response, "OTP not found. Please resend OTP.")

    def test_reset_password_user_not_found(self):
        self.set_reset_session("unknown@example.com")

        response = self.client.post(
            reverse("forgot_password"),
            {
                "reset_password": "1",
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        self.assertEqual(response.status_code, 200)


class ProjectViewSetTests(BaseTestCase):
    """Tests for ProjectModelViewSet."""

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    def test_authenticated_queryset(self):
        request = self.factory.get("/users/")
        request.user = self.user

        view = self.get_view(request)
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user)

    def test_anonymous_queryset(self):
        request = self.factory.get("/users/")
        request.user = AnonymousUser()

        view = self.get_view(request)
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 0)
