from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Users(models.Model):
    """Stores user profile information"""

    username = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=50, null=True)
    number = models.CharField(max_length=10, null=True, blank=True)
    other_number = models.CharField(max_length=10, null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True)
    password = models.CharField(max_length=20, null=True)
    profile_image = models.ImageField(upload_to="profile/", default="default.png")

    owner = models.ForeignKey(
        User, related_name="snippets", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        """Returns the username as the string representation."""
        return self.username


class Contact(models.Model):
    """Stores contact form details submitted by users."""

    name = models.CharField(max_length=20, null=True)
    email = models.CharField(null=True)
    message = models.TextField(max_length=200, null=True)

    def __str__(self):
        """Returns the contact name as the string representation."""
        return self.name
