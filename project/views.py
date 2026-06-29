import re
from datetime import date

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from project.models import Contact, Users
from project.permissions import IsOwnerOrReadOnly
from project.serializers import ContactSerializer, UsersModelSerializer


def project_list(request):
    projects = Users.objects.all()
    return render(request, "dashboard.html", {"projects": projects})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        number = request.POST.get("number")
        other_number = request.POST.get("other_number")
        date_birth = request.POST.get("date_birth")
        address = request.POST.get("address")
        password = request.POST.get("password")

        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", username):
            return HttpResponse("Invalid Username")

        if not re.match(
            r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$", password
        ):
            return HttpResponse("Invalid Password")

        if User.objects.filter(username=username).exists():

            return render(
                request, "register.html", {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        user.save()
        Users.objects.create(
            owner=user,
            username=username,
            email=email,
            number=number,
            other_number=other_number,
            date_birth=date_birth,
            address=address,
            password=password,
        )
        return redirect("login")
    return render(request, "register.html", {"today_date": date.today().isoformat()})


@login_required(login_url="login")
def dashboard(request):
    projects = request.session.get("username")
    return render(request, "dashboard.html", {"project": projects})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session["username"] = username
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url="login")
def profile(request):

    users = Users.objects.filter(owner=request.user).first()
    if not users:
        return render(request, "profile.html", {"error": "Profile not found"})

    if users.owner == request.user:

        if request.method == "POST":
            users.username = request.POST.get("username")
            users.number = request.POST.get("number")
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
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully")

            users.save()

            return redirect("profile")

    return render(
        request,
        "profile.html",
        {"users": users, "today_date": date.today().isoformat()},
    )


def logoutpage(request):
    logout(request)
    return render(request, "login.html")


def services(request):
    return render(request, "services.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            message=message,
        )
    return render(request, "contact.html")


def forgot_password(request):
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
            return redirect("login")
        except User.DoesNotExist:
            return render(request, "forgot_password.html", {"error": "Invalid Email"})
    return render(request, "forgot_password.html")


class ProjectModelViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class ContactModelViewSet(ModelViewSet):

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
