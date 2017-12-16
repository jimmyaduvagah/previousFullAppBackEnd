from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from attachments.permissions import IsAllowedOrSuperuser
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from quiz.models import Quiz
from quiz.serializers import QuizSerializer, UserAnswersQuizSerializer


class QuizViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    full_serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    @detail_route(methods=['PUT'])
    def check(self, request, *args, **kwargs):
        self.permission_classes = (IsAuthenticated,)
        quiz = self.get_object()

        self.serializer_class = UserAnswersQuizSerializer

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            total_questions = len(quiz.object)
            total_correct_questions = 0
            to_return = serializer.validated_data
            to_return['percent_correct'] = 0

            for question in quiz.object:
                for chosen_answer in to_return['chosen_answers']:
                    if chosen_answer['question_uuid'] == question['uuid']:
                        chosen_answer['correct'] = False
                        if chosen_answer['answer_uuid'] == question['answer_uuid']:
                            chosen_answer['correct'] = True
                            total_correct_questions += 1

            to_return['percent_correct'] = total_correct_questions / total_questions


        response = Response(to_return)
        return response

    def update(self, request, *args, **kwargs):
        raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        raise PermissionDenied()
