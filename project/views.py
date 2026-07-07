# Standard library imports
import logging
import random
import re
from datetime import date

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
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

# Third-party imports
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

# Local application imports
from project.models import ContactInfo, ContactMessage, CustomUser
from project.permissions import IsOwnerOrReadOnly
from project.serializers import ContactSerializer, UsersModelSerializer

from .forms import ProfileForm, RegisterForm, SetNewPasswordForm

# Temporary OTP store (demo purpose)
OTP_STORE = {}

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

            logger.info("User registered successfully: %s", user.username)

            return redirect("login")

        logger.warning("Registration form validation failed.")

        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    else:
        form = RegisterForm()

    return render(
        request,
        "register.html",
        {"form": form, "today_date": date.today().isoformat()},
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

    if not user:
        logger.warning("Profile not found for %s", request.user.username)
        return render(request, "profile.html", {"error": "Profile not found"})

    if request.method == "POST":

        form = ProfileForm(request.POST, user=request.user)

        if form.is_valid():

            user.username = form.cleaned_data["username"]
            user.mobile_number = form.cleaned_data["mobile_number"]
            user.other_mobile_number = form.cleaned_data["other_mobile_number"]
            user.date_birth = form.cleaned_data["date_birth"]
            user.address = form.cleaned_data["address"]

            if request.FILES.get("profile_image"):
                user.profile_image = request.FILES.get("profile_image")

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
                "other_mobile_number": (user.other_mobile_number),
                "date_birth": user.date_birth,
                "address": user.address,
            },
            user=request.user,
        )

    return render(
        request,
        "profile.html",
        {
            "user": user,
            "form": form,
            "today_date": date.today().isoformat(),
        },
    )


def logoutpage(request: HttpRequest) -> HttpResponse:
    """Logout current user and redirect to login page."""
    logger.info("User logged out: %s", request.user.username)
    logout(request)
    messages.error(request, "Logout successfully!")
    return redirect("login")


def services(request: HttpRequest) -> HttpResponse:
    """Render services page."""
    return render(request, "services.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Handle contact form submission and display contact info."""
    contact_info = ContactInfo.objects.first()

    if request.method == "POST":
        serializer = ContactSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Contact form submitted by %s", serializer.validated_data["email"]
            )
            return redirect("contact")

        for error in serializer.errors.values():
            messages.error(request, error)

    return render(request, "contact.html", {"contact_info": contact_info})


def forgot_password(request):

    step = "step1"
    form = None

    # STEP 1: SEND OTP
    if request.method == "POST" and "send_otp" in request.POST:

        email = request.POST.get("email")

        if not User.objects.filter(email=email).exists():
            messages.error(request, "Invalid email")
            step = "step1"

        else:
            otp = str(random.randint(100000, 999999))
            OTP_STORE[email] = otp

            print("OTP:", otp)

            send_mail(
                "Your OTP",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            request.session["reset_email"] = email
            step = "step2"

            messages.success(request, "OTP sent successfully")

    # STEP 2: VERIFY OTP
    elif request.method == "POST" and "verify_otp" in request.POST:

        email = request.session.get("reset_email")
        otp_input = request.POST.get("otp")

        if email and OTP_STORE.get(email) == otp_input:
            step = "step3"
            messages.success(request, "OTP verified")

        else:
            step = "step2"
            messages.error(request, "Invalid OTP")

    # STEP 3: RESET PASSWORD
    elif request.method == "POST" and "reset_password" in request.POST:

        email = request.session.get("reset_email")
        form = SetNewPasswordForm(request.POST)

        if form.is_valid():

            new_password = form.cleaned_data["new_password"]

            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            OTP_STORE.pop(email, None)
            request.session.pop("reset_email", None)

            messages.success(request, "Password reset successful")
            return redirect("login")

        else:
            messages.error(request, "Password invalid or does not match")
            step = "step3"

    # GET REQUEST (or reload step 3 form)
    if step == "step3":
        form = SetNewPasswordForm()

    return render(request, "forgot_password.html", {"step": step, "form": form})


class ProjectModelViewSet(ModelViewSet):
    """API ViewSet for performing CRUD operations on CustomUser."""

    queryset = CustomUser.objects.all()
    serializer_class = UsersModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ContactModelViewSet(ModelViewSet):
    """API ViewSet for handling ContactMessage CRUD operations."""

    queryset = ContactMessage.objects.all()
    serializer_class = ContactSerializer
