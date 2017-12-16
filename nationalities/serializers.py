from rest_framework.fields import ReadOnlyField

from .models import Nationality
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers


class NationalitySerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Nationality
        fields = ('id', 'name', 'slug')

    slug = ReadOnlyField()


