from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .validators import validate_phone_number, validate_username


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

    username = models.CharField(
        max_length=16, unique=True, validators=[validate_username]
    )
    mobile_number = models.CharField(
        max_length=15, null=True, blank=True, validators=[validate_phone_number]
    )
    other_mobile_number = models.CharField(
        max_length=15, null=True, blank=True, validators=[validate_phone_number]
    )
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
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number])
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


class PasswordResetOTP(models.Model):
    """
    Stores a One-Time Password (OTP) used for password reset verification.

    Fields:
        email (EmailField): Email address of the user requesting the password reset.
        otp (CharField): Six-digit OTP sent to the user's email.
        created_at (DateTimeField): Timestamp when the OTP record was created.
        expiry (DateTimeField): Timestamp indicating when the OTP expires.
    """

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expiry

    def __str__(self):
        return self.email
