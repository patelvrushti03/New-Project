# Standard library imports
import logging
import random
from datetime import date, timedelta

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

# Third-party imports
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

# Local application imports
from project.models import ContactInfo, ContactMessage, CustomUser, PasswordResetOTP
from project.permissions import IsOwnerOrReadOnly
from project.serializers import UsersModelSerializer
from project.validators import validate_contact_email

from .forms import ProfileForm, RegisterForm, SetNewPasswordForm

# Initialize logger for application logging.
logger = logging.getLogger(__name__)
User = get_user_model()


def register(request: HttpRequest) -> HttpResponse:
    """Handle user registration, validation, and profile creation."""
    logger.info("Registration request received")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                mobile_number=form.cleaned_data["mobile_number"],
                other_mobile_number=form.cleaned_data["other_mobile_number"],
                date_birth=form.cleaned_data["date_birth"],
                address=form.cleaned_data["address"],
            )

            messages.success(request, "User registered successfully.")

            return redirect("login")

        logger.warning("Registration form validation failed.")

        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    else:
        form = RegisterForm()

    return render(
        request, "register.html", {"form": form, "today_date": date.today().isoformat()}
    )


def user_login(request: HttpRequest) -> HttpResponse:
    """Check username and password. If correct, log the user in and redirect to the dashboard page."""
    logger.info("Login page accessed")
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        logger.info("Login attempt for username: %s", username)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info("User logged in successfully: %s", username)
            return redirect("dashboard")
        else:
            logger.warning("Invalid login attempt: %s", username)
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url="login")
def dashboard(request: HttpRequest) -> HttpResponse:
    """Display dashboard page for logged-in user."""
    logger.info("Dashboard opened by %s", request.user.username)
    return render(request, "dashboard.html")


@login_required(login_url="login")
def profile(request: HttpRequest) -> HttpResponse:
    """Display and update user profile including password change."""
    user = request.user

    if request.method == "POST":

        form = ProfileForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            user.mobile_number = form.cleaned_data["mobile_number"]
            user.other_mobile_number = form.cleaned_data["other_mobile_number"]
            user.date_birth = form.cleaned_data["date_birth"]
            user.address = form.cleaned_data["address"]

            profile_image = form.cleaned_data.get("profile_image")
            if profile_image:
                user.profile_image = profile_image

            if form.cleaned_data["new_password"]:
                request.user.set_password(
                    form.cleaned_data["new_password"],
                )
                request.user.save()
                update_session_auth_hash(request, request.user)
                logger.info(
                    "Password changed successfully for %s", request.user.username
                )
                messages.success(request, "Password changed successfully.")

            user.save()
            logger.info("Profile updated by %s", request.user.username)

            return redirect("profile")

        logger.warning("Profile form validation failed for %s", request.user.username)

        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    else:
        form = ProfileForm(
            initial={
                "username": user.username,
                "mobile_number": user.mobile_number,
                "other_mobile_number": user.other_mobile_number,
                "date_birth": user.date_birth,
                "address": user.address,
            },
            user=request.user,
        )

    return render(
        request,
        "profile.html",
        {"user": user, "form": form, "today_date": date.today().isoformat()},
    )


def logoutpage(request: HttpRequest) -> HttpResponse:
    """Logout current user and redirect to login page."""
    logger.info("User logged out: %s", request.user.username)
    logout(request)
    messages.success(request, "Logout successfully!")
    return redirect("login")


def services(request: HttpRequest) -> HttpResponse:
    """Render services page."""
    return render(request, "services.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Handle contact form submission and display contact info."""
    contact_info = ContactInfo.objects.first()

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        try:
            validate_contact_email(email)
        except ValidationError as e:
            messages.error(request, e.message)
            return render(request, "contact.html", {"contact_info": contact_info})

        if email.lower() != request.user.email.lower():
            messages.error(request, "Please enter your registered email address.")
            return render(request, "contact.html", {"contact_info": contact_info})

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
        )

        messages.success(request, "Your message has been sent successfully.")
        return redirect("contact")

    return render(request, "contact.html", {"contact_info": contact_info})


def forgot_password(request: HttpRequest) -> HttpResponse:
    """Handle forgot password process using database stored OTP."""
    step = "step1"
    form = None

    # STEP 1 : SEND / RESEND OTP
    if request.method == "POST" and (
        "send_otp" in request.POST or "resend_otp" in request.POST
    ):

        if "send_otp" in request.POST:
            email = request.POST.get("email")

            if not User.objects.filter(email=email).exists():
                messages.error(request, "Invalid email")
                return render(request, "forgot_password.html", {"step": "step1"})

            request.session["reset_email"] = email

        else:
            email = request.session.get("reset_email")

            if not email:
                messages.error(request, "Session expired. Please enter email again.")
                return render(request, "forgot_password.html", {"step": "step1"})

        PasswordResetOTP.cleanup_expired()

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.filter(email=email).delete()

        PasswordResetOTP.objects.create(
            email=email,
            otp=otp,
            expiry=timezone.now() + timedelta(seconds=60),
        )

        try:
            send_mail(
                "Your OTP",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.exception("Failed to send OTP email: %s", exc)
            messages.error(
                request, "Unable to send OTP at the moment. Please try again later."
            )
            return redirect("forgot_password")

        step = "step2"

        if "send_otp" in request.POST:
            messages.success(request, "OTP sent successfully.")
        else:
            messages.success(request, "OTP resent successfully.")

    # STEP 2 : VERIFY OTP
    elif request.method == "POST" and "verify_otp" in request.POST:

        email = request.session.get("reset_email")
        otp_input = request.POST.get("otp")

        otp_data = PasswordResetOTP.objects.filter(email=email).first()

        if not otp_data:
            step = "step2"
            messages.error(request, "OTP not found. Please resend OTP.")
        elif otp_data.is_expired():
            otp_data.delete()
            step = "step2"
            messages.error(request, "OTP has expired. Please click Resend OTP.")
        elif otp_data.otp == otp_input:
            step = "step3"
            messages.success(request, "OTP verified.")
        else:
            step = "step2"
            messages.error(request, "Invalid OTP.")

    # STEP 3 : RESET PASSWORD
    elif request.method == "POST" and "reset_password" in request.POST:
        email = request.session.get("reset_email")
        form = SetNewPasswordForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user = User.objects.filter(email=email).first()

            if user:
                user.set_password(new_password)
                user.save()

                PasswordResetOTP.objects.filter(email=email).delete()

                request.session.pop("reset_email", None)
                messages.success(request, "Password reset successful.")
                return redirect("login")
        else:
            step = "step3"
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    if step == "step3":
        form = SetNewPasswordForm()

    return render(request, "forgot_password.html", {"step": step, "form": form})


class ProjectModelViewSet(ModelViewSet):
    """API ViewSet for performing CRUD operations on CustomUser."""

    queryset = CustomUser.objects.all()
    serializer_class = UsersModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
