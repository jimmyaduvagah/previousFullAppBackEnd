from rest_framework.fields import ReadOnlyField

from .models import Town
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers


class TownSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Town
        fields = ('id', 'name', 'slug')

    slug = ReadOnlyField()


