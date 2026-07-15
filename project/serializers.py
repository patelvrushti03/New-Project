from rest_framework import serializers

from project.models import CustomUser


class UsersModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "mobile_number",
            "other_mobile_number",
            "date_birth",
            "address",
        ]
