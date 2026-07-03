import logging
import re
from datetime import date

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from project.models import ContactInfo, ContactMessage, UserProfile
from project.permissions import IsOwnerOrReadOnly
from project.serializers import ContactSerializer, UsersModelSerializer

logger = logging.getLogger(__name__)


def register(request: HttpRequest) -> HttpResponse:
    """Handle user registration, validation, and profile creation."""
    logger.info("Registration request received")
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        other_mobile_number = request.POST.get("other_mobile_number")
        date_birth = request.POST.get("date_birth")
        address = request.POST.get("address")
        password = request.POST.get("password")

        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", username):
            logger.warning("Invalid username format: %s", username)
            messages.error(
                request,
                "Username must be 3 to 16 characters long and contain only letters, numbers, and underscores.",
            )
            return redirect("register")

        if not re.match(r"^\+?[0-9]{6,15}$", mobile_number):
            logger.warning("Invalid mobile number for username: %s", username)
            messages.error(request, "Please enter a valid phone number.")
            return redirect("register")

        if other_mobile_number and not re.match(
            r"^\+?[0-9]{6,15}$", other_mobile_number
        ):
            logger.warning("Invalid mobile number for username: %s", username)
            messages.error(request, "Please enter a valid phone number.")
            return redirect("register")

        if not re.match(
            r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$", password
        ):
            logger.warning("Invalid password format for username: %s", username)
            messages.error(
                request,
                "Password must contain an uppercase letter, lowercase letter, number, and special character.",
            )
            return redirect("register")

        if User.objects.filter(username=username).exists():
            logger.warning("Username already exists: %s", username)
            return render(
                request, "register.html", {"error": "Username already exists"}
            )

        if User.objects.filter(email=email).exists():
            logger.warning("Registration failed. Email already exists: %s", email)
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        UserProfile.objects.create(
            owner=user,
            username=username,
            email=email,
            mobile_number=mobile_number,
            other_mobile_number=other_mobile_number,
            date_birth=date_birth,
            address=address,
        )
        logger.info("User registered successfully: %s", username)

        return redirect("login")
    return render(request, "register.html", {"today_date": date.today().isoformat()})


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
    user_profile = UserProfile.objects.filter(owner=request.user).first()

    if not user_profile:
        logger.warning("Profile not found for %s", request.user.username)
        return render(request, "profile.html", {"error": "Profile not found"})

    if request.method == "POST":
        user_profile.username = request.POST.get("username")
        user_profile.mobile_number = request.POST.get("mobile_number")
        user_profile.other_mobile_number = request.POST.get("other_mobile_number")
        user_profile.date_birth = request.POST.get("date_birth")
        user_profile.address = request.POST.get("address")
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if request.FILES.get("profile_image"):
            user_profile.profile_image = request.FILES.get("profile_image")

        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", user_profile.username):
            messages.error(request, "Invalid Username")
            return redirect("profile")

        if not re.match(r"^\+?[0-9]{6,15}$", user_profile.mobile_number):
            logger.warning(
                "Invalid mobile number for username: %s", user_profile.username
            )
            messages.error(request, "Please enter a valid phone number.")
            return redirect("profile")

        if user_profile.other_mobile_number and not re.match(
            r"^\+?[0-9]{6,15}$", user_profile.other_mobile_number
        ):
            logger.warning(
                "Invalid mobile number for username: %s", user_profile.username
            )
            messages.error(request, "Please enter a valid phone number.")
            return redirect("profile")

        if old_password or new_password or confirm_password:
            if not old_password:
                messages.error(request, "Please enter old password")
                return redirect("profile")
            if not new_password:
                messages.error(request, "Please enter new password")
                return redirect("profile")
            if not confirm_password:
                messages.error(request, "Please enter confirm password")
                return redirect("profile")
            if not request.user.check_password(old_password):
                messages.error(request, "old password is incorrect")
                return redirect("profile")
            if new_password == old_password:
                messages.error(request, "new password do not change")
                return redirect("profile")
            if new_password != confirm_password:
                messages.error(request, "new password do not match confirm password")
                return redirect("profile")
            if not re.match(
                r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$",
                new_password,
            ):
                messages.error(
                    request,
                    "Password must contain uppercase, lowercase, number and special character",
                )
                return redirect("profile")
            request.user.set_password(new_password)
            request.user.save()
            logger.info("Password changed successfully for %s", request.user.username)
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully")
        logger.info("Profile updated by %s", request.user.username)
        user_profile.save()
        return redirect("profile")

    return render(
        request,
        "profile.html",
        {"user_profile": user_profile, "today_date": date.today().isoformat()},
    )


def logoutpage(request: HttpRequest) -> HttpResponse:
    """Logout current user and redirect to login page."""
    logger.info("User logged out: %s", request.user.username)
    logout(request)
    messages.error(
        request,
        "Logout successfully!",
    )
    return redirect("login")


def services(request: HttpRequest) -> HttpResponse:
    """Render services page."""
    return render(request, "services.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Handle contact form submission and display contact info."""
    contact_info = ContactInfo.objects.first()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
        )
        logger.info("Contact form submitted by %s", email)
    return render(
        request,
        "contact.html",
        {"contact_info": contact_info},
    )


def forgot_password(request: HttpRequest) -> HttpResponse:
    """Reset user password using email verification."""
    logger.info("Password reset request received")
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        try:
            user = User.objects.get(email=email)
            if new_password != confirm_password:
                messages.error(request, "new password do no match confirm password")
                return redirect("forgot_password")

            if not re.match(
                r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$", new_password
            ):
                messages.error(
                    request,
                    "Password must contain uppercase, lowercase, number and special character",
                )
                return redirect("forgot_password")

            user.set_password(new_password)
            user.save()
            logger.info("Password reset successful for %s", email)
            return redirect("login")
        except User.DoesNotExist:
            logger.warning("Password reset failed. Email not found: %s", email)
            return render(request, "forgot_password.html", {"error": "Invalid Email"})
    return render(request, "forgot_password.html")


class ProjectModelViewSet(ModelViewSet):
    """API ViewSet for performing CRUD operations on UserProfile."""

    queryset = UserProfile.objects.all()
    serializer_class = UsersModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ContactModelViewSet(ModelViewSet):
    """API ViewSet for handling ContactMessage CRUD operations."""

    queryset = ContactMessage.objects.all()
    serializer_class = ContactSerializer
