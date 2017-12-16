from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotAcceptable, PermissionDenied, MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from attachments.permissions import IsAllowedOrSuperuser
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from quizzes.models import Quiz, QuizQuestion, QuizQuestionAnswer
from quizzes.serializers import QuizSerializer, QuizQuestionAnswerSerializer, QuizQuestionSerializer
from twz_server_django.utils import log_action


class QuizViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    full_serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['questions'] = QuizQuestionSerializer(QuizQuestion.objects.filter(quiz=instance), many=True).data
        for question in data['questions']:
            question['answers'] = QuizQuestionAnswerSerializer(
                QuizQuestionAnswer.objects.filter(quiz_question=question['id']), many=True).data

        return Response(data)

    # @detail_route(methods=['PUT'])
    # def check(self, request, *args, **kwargs):
    #     self.permission_classes = (IsAuthenticated,)
    #     quiz = self.get_object()
    #
    #     self.serializer_class = UserAnswersQuizSerializer
    #
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         total_questions = len(quiz.object)
    #         total_correct_questions = 0
    #         to_return = serializer.validated_data
    #         to_return['percent_correct'] = 0
    #
    #         for question in quiz.object:
    #             for chosen_answer in to_return['chosen_answers']:
    #                 if chosen_answer['question_uuid'] == question['uuid']:
    #                     chosen_answer['correct'] = False
    #                     if chosen_answer['answer_uuid'] == question['answer_uuid']:
    #                         chosen_answer['correct'] = True
    #                         total_correct_questions += 1
    #
    #         to_return['percent_correct'] = total_correct_questions / total_questions
    #
    #
    #     response = Response(to_return)
    #     return response

    def update(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizViewSet, self).create(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizViewSet, self).delete(request, *args, **kwargs)
        else:
            raise PermissionDenied()


class QuizQuestionViewSet(CreatedModifiedByModelViewSetMixin):
    """

    __reorder__ [PUT]:

    A batch reorder method, simply send an array of objects with `{"id":"","order":""}`


    """
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    full_serializer_class = QuizQuestionSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    def update(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])
            return super(QuizQuestionViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizQuestionViewSet, self).create(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizQuestionViewSet, self).delete(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    @list_route(methods=['put'])
    def reorder(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            id_list = []
            list = request.data
            for item in list:
                id_list.append(item['id'])
                obj = self.get_queryset().get(id=item['id'])
                obj.to(item['order'])
                qs = self.get_queryset().filter(id__in=id_list)

            return Response(self.get_serializer(qs, many=True).data)

        raise MethodNotAllowed('PUT')

class QuizQuestionAnswerViewSet(CreatedModifiedByModelViewSetMixin):
    """

    __reorder__ [PUT]:

    A batch reorder method, simply send an array of objects with `{"id":"","order":""}`


    """
    queryset = QuizQuestionAnswer.objects.all()
    serializer_class = QuizQuestionAnswerSerializer
    full_serializer_class = QuizQuestionAnswerSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    def update(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])
            return super(QuizQuestionAnswerViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def create(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizQuestionAnswerViewSet, self).create(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        log_action(request)
        if request.user.is_superuser or request.user.is_staff:
            return super(QuizQuestionAnswerViewSet, self).delete(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    @list_route(methods=['put'])
    def reorder(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            id_list = []
            list = request.data
            for item in list:
                id_list.append(item['id'])
                obj = self.get_queryset().get(id=item['id'])
                obj.to(item['order'])
                qs = self.get_queryset().filter(id__in=id_list)

            return Response(self.get_serializer(qs, many=True).data)

        raise MethodNotAllowed('PUT')

