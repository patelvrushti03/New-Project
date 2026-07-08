import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

PHONE_REGEX = r"^\+?[0-9]{10,15}$"
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,16}$"
PASSWORD_REGEX = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$"


def validate_phone_number(phone_number):
    """Validate phone number."""
    if phone_number and not re.match(PHONE_REGEX, phone_number):
        raise ValidationError("Invalid phone number.")
    return phone_number


def validate_username(username):
    """Validate username."""
    if username and not re.match(USERNAME_REGEX, username):
        raise ValidationError("Invalid username.")
    return username


def validate_password_format(password):
    """Validate password."""
    if password and not re.match(PASSWORD_REGEX, password):
        raise ValidationError(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, one special character "
            "and be at least 6 characters long."
        )
    return password


def validate_contact_email(email):
    """Validate contact email."""
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Please enter a valid email address.")
    return email
