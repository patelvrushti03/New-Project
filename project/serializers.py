from rest_framework import serializers

from project.models import Contact, Users


class UsersModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = [
            "url",
            "username",
            "email",
            "number",
            "other_number",
            "date_birth",
            "address",
            "owner",
        ]

    owner = serializers.ReadOnlyField(source="owner.username")


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "name",
            "email",
            "message",
        ]
