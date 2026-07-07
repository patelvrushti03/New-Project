from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending Django AbstractUser.
    Stores detailed user information for the application.

    Fields:
        mobile_number (CharField): Primary mobile number.
        other_mobile_number (CharField): Alternate contact number.
        date_birth (DateField): User's date of birth.
        address (TextField): Full address of the user.
        profile_image (ImageField): Profile image of user.
    """

    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    other_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile/", default="default.png", blank=True
    )

    def __str__(self):
        """Return username of the user."""
        return self.username


class ContactInfo(models.Model):
    """
    Stores contact information for the application.

    Fields:
        email (EmailField): Contact email address.
        phone_number (CharField): Contact phone number.
        location (CharField): Physical location (optional).
    """

    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        """Return email of contact info."""
        return self.email


class ContactMessage(models.Model):
    """
    Stores messages submitted through contact form.

    Fields:
        name (CharField): Name of the sender.
        email (EmailField): Email address of sender.
        message (TextField): Message submitted by the sender.
    """

    name = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    message = models.TextField(max_length=200, null=True)

    def __str__(self):
        """Return name of message sender."""
        return self.name
