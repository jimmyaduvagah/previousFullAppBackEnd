from rest_framework import serializers

from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2
from media.models import Media


class MediaSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Media

    module_id = serializers.UUIDField()

    quiz = QuizSerializer()
    quiz_id = serializers.UUIDField()