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
