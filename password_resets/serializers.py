from rest_framework import serializers
from drf_users.serializers import UserSerializer, UserFullSerializer
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializer
from .models import PasswordResetToken


#  View Serializers

class PasswordResetTokenSerializer(P33ModelSerializer):
    class Meta:
        model = PasswordResetToken
