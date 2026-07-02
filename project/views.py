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
        other_number = request.POST.get("other_number")
        date_birth = request.POST.get("date_birth")
        address = request.POST.get("address")
        password = request.POST.get("password")

        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", username):
            logger.warning(f"Invalid username format: {username}")
            return HttpResponse("Invalid Username")

        if not re.match(
            r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$", password
        ):
            logger.warning(f"Invalid password format for username: {username}")
            return HttpResponse("Invalid Password")

        if User.objects.filter(username=username).exists():
            logger.warning(f"Username already exists: {username}")
            return render(
                request, "register.html", {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        user.save()
        UserProfile.objects.create(
            owner=user,
            username=username,
            email=email,
            mobile_number=mobile_number,
            other_number=other_number,
            date_birth=date_birth,
            address=address,
        )
        logger.info(f"User registered successfully: {username}")

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

        logger.info(f"Login attempt for username: {username}")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"User logged in successfully: {username}")
            return redirect("dashboard")
        else:
            logger.warning(f"Invalid login attempt: {username}")
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url="login")
def dashboard(request: HttpRequest) -> HttpResponse:
    """Display dashboard page for logged-in user."""
    logger.info(f"Dashboard opened by {request.user.username}")
    return render(request, "dashboard.html")


@login_required(login_url="login")
def profile(request: HttpRequest) -> HttpResponse:
    """Display and update user profile including password change."""
    users = UserProfile.objects.filter(owner=request.user).first()

    if not users:
        logger.warning(f"Profile not found for {request.user.username}")
        return render(request, "profile.html", {"error": "Profile not found"})

    if users.owner == request.user:

        if request.method == "POST":
            users.username = request.POST.get("username")
            users.mobile_number = request.POST.get("mobile_number")
            users.other_number = request.POST.get("other_number")
            users.date_birth = request.POST.get("date_birth")
            users.address = request.POST.get("address")

            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if request.FILES.get("profile_image"):
                users.profile_image = request.FILES.get("profile_image")

            if not re.match(r"^[a-zA-Z0-9_]{3,16}$", users.username):
                messages.error(request, "Invalid Username")
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
                    messages.error(
                        request, "new password do not match confirm password"
                    )
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
                logger.info(
                    f"Password changed successfully for {request.user.username}"
                )
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully")

            logger.info(f"Profile updated by {request.user.username}")
            users.save()

            return redirect("profile")

    return render(
        request,
        "profile.html",
        {"users": users, "today_date": date.today().isoformat()},
    )


def logoutpage(request: HttpRequest) -> HttpResponse:
    """Logout current user and redirect to login page."""
    logger.info(f"User logged out: {request.user.username}")
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
        logger.info(f"Contact form submitted by {email}")
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
            logger.info(f"Password reset successful for {email}")
            return redirect("login")
        except User.DoesNotExist:
            logger.warning(f"Password reset failed. Email not found: {email}")
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
