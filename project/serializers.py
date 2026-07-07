import re

from rest_framework import serializers

from project.models import ContactMessage, CustomUser


class UsersModelSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = CustomUser
        fields = [
            "url",
            "username",
            "email",
            "mobile_number",
            "other_mobile_number",
            "date_birth",
            "address",
            "owner",
        ]

    def validate_username(self, value):
        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", value):
            raise serializers.ValidationError("Invalid username format")
        return value


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "message",
        ]

    def validate(self, data):
        if not data.get("name") or not data.get("email") or not data.get("message"):
            raise serializers.ValidationError("All fields are required.")
        return data
