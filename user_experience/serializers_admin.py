
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers
from .models import UserProfileExperience, UserProfileExperienceType

class UserProfileExperienceAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperience

class UserProfileExperienceTypeAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperienceType
