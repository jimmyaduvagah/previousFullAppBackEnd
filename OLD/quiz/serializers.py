from rest_framework import serializers
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2
from quiz.models import Quiz


class QuizSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Quiz


class UserAnswersQuizSerializer(serializers.Serializer):
    class Meta:
        fields = ('chosen_answers',)

    chosen_answers = serializers.JSONField(read_only=False, required=True)
