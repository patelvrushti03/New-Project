from rest_framework import serializers

from project.models import Contact, Project


class ProjectModelSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "url",
            "username",
            "email",
            "number",
            "other_num",
            "Date_birth",
            "Address",
            "owner",
        ]

    owner = serializers.ReadOnlyField(source="owner.username")

    def get_owner(self, obj):
        if obj.owner:
            return obj.owner.username
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "name",
            "email",
            "message",
        ]
