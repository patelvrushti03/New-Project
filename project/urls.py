from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("projects/", views.project_list, name="projects"),
    path("profile/", views.profile, name="profile"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("logout/", views.logoutpage, name="logout"),
]
