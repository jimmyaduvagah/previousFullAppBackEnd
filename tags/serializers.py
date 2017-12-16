from rest_framework import serializers

from tags.models import Tag
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2


class TagSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Tag
        fields = ('id', 'title')

    title = serializers.CharField(required=True)
