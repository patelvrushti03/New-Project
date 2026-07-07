# Standard library imports
import re
from datetime import date

# Django imports
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

PHONE_REGEX = r"^\+?[0-9]{10,15}$"
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,16}$"
PASSWORD_REGEX = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$"


def validate_username(username):
    """Validate username."""
    if not re.match(USERNAME_REGEX, username):
        raise forms.ValidationError(
            "Username must be 3 to 16 characters long and contain only letters, numbers, and underscores."
        )
    return username


def validate_phone_number(phone_number):
    """Validate phone number."""
    if phone_number and not re.match(PHONE_REGEX, phone_number):
        raise forms.ValidationError("Phone number must contain 10 to 15 digits.")

    return phone_number


def validate_date_birth(date_birth):
    """Validate date of birth."""
    if date_birth and date_birth > date.today():
        raise forms.ValidationError("Date of birth cannot be in the future.")
    return date_birth


def validate_password(password):
    """Validate password."""
    if not re.match(
        PASSWORD_REGEX,
        password,
    ):
        raise forms.ValidationError(
            "Password must contain an uppercase letter, lowercase letter, number, and special character."
        )
    return password


class RegisterForm(forms.Form):
    """Registration form."""

    username = forms.CharField(max_length=16)
    email = forms.EmailField()
    mobile_number = forms.CharField(max_length=15)
    other_mobile_number = forms.CharField(required=False, max_length=15)
    date_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "max": date.today().isoformat()}),
    )
    address = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        username = validate_username(self.cleaned_data["username"])

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    def clean_mobile_number(self):
        return validate_phone_number(self.cleaned_data["mobile_number"])

    def clean_other_mobile_number(self):
        return validate_phone_number(self.cleaned_data["other_mobile_number"])

    def clean_date_birth(self):
        return validate_date_birth(self.cleaned_data["date_birth"])

    def clean_password(self):
        return validate_password(self.cleaned_data["password"])


class ProfileForm(forms.Form):
    """Profile update form."""

    username = forms.CharField(max_length=16)
    mobile_number = forms.CharField(max_length=15)
    other_mobile_number = forms.CharField(required=False, max_length=15)
    date_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "max": date.today().isoformat()}),
    )

    address = forms.CharField(required=False)
    old_password = forms.CharField(required=False, widget=forms.PasswordInput())
    new_password = forms.CharField(required=False, widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        return validate_username(self.cleaned_data["username"])

    def clean_mobile_number(self):
        return validate_phone_number(self.cleaned_data["mobile_number"])

    def clean_other_mobile_number(self):
        return validate_phone_number(self.cleaned_data["other_mobile_number"])

    def clean_date_birth(self):
        return validate_date_birth(self.cleaned_data["date_birth"])

    def clean(self):
        cleaned_data = super().clean()

        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if old_password or new_password or confirm_password:

            if not old_password:
                raise forms.ValidationError("Please enter old password.")

            if not new_password:
                raise forms.ValidationError("Please enter new password.")

            if not confirm_password:
                raise forms.ValidationError("Please enter confirm password.")

            if not self.user.check_password(old_password):
                raise forms.ValidationError("Old password is incorrect.")

            if new_password == old_password:
                raise forms.ValidationError(
                    "New password must be different from old password."
                )

            new_password = validate_password(new_password)

            if new_password != confirm_password:
                raise forms.ValidationError(
                    "New password and confirm password do not match."
                )

        return cleaned_data


# Step 1: Email form
class ForgotPasswordEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Invalid Email.")
        return email


# Step 2: OTP form
class OTPVerifyForm(forms.Form):
    otp = forms.CharField(max_length=6)


# Step 3: New password form
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
