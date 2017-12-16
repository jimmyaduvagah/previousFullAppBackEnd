from django.contrib.auth.models import Group
from rest_framework import serializers

from drf_users.models import InvitationCode
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from .models import User

class UserAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class InvitationCodeAdminSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = InvitationCode

