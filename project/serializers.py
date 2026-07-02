from rest_framework import serializers

from project.models import ContactMessage, UserProfile


class UsersModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
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

    owner = serializers.ReadOnlyField(source="owner.username")


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "message",
        ]
