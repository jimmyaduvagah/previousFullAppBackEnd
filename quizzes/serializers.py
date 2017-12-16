from rest_framework import serializers

from quizzes.models import Quiz, QuizQuestion, QuizQuestionAnswer
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2, CreatedModifiedByModelSerializer


class QuizQuestionAnswerSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = QuizQuestionAnswer
        fields = '__all__'

    quiz_question_id = serializers.UUIDField()


class QuizQuestionSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = QuizQuestion
        fields = '__all__'

    answers = QuizQuestionAnswerSerializer(source='quizquestionanswer_set.all', many=True, read_only=True)
    quiz_id = serializers.UUIDField()
    correct_answer_id = serializers.UUIDField(required=False)


class QuizSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = Quiz
        fields = '__all__'

    quiz_questions = QuizQuestionSerializer(source='quizquestion_set.all', many=True, read_only=True)
