from .models import Attachment
from rest_framework import serializers
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer


class AttachmentSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Attachment

    filename = serializers.CharField(read_only=True)