from links.models import Link
from rest_framework import serializers

from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer, P33ModelSerializer


class LinkSerializer(P33ModelSerializer):
    class Meta:
        model = Link
        fields = ('id', 'data')

