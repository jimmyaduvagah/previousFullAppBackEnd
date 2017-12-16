from django.core.exceptions import PermissionDenied
from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated

from assessments.models import Assessment
from assessments.serializers import AssessmentSerializer, AssessmentFullSerializer
from courses.models import CourseProgress
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from twz_server_django.utils import log_action


class AssessmentViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    full_serializer_class  = AssessmentFullSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        course_progress_id = request.GET.get('course_progress_id', None)
        if course_progress_id:
            self.queryset = self.queryset.filter(course_progress_id=course_progress_id)

        response = super(AssessmentViewSet, self).list(request, *args, **kwargs)
        log_action(request)
        return response


    def retrieve(self, request, *args, **kwargs):
        response = super(AssessmentViewSet, self).retrieve(request, *args, **kwargs)
        log_action(request, self.get_object())
        return response

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied()

    def update(self, request, *args, **kwargs):
        response = super(AssessmentViewSet, self).update(request, *args, **kwargs)
        log_action(request, self.get_object())
        return response

    def create(self, request, *args, **kwargs):
        course_progress_id = request.data.get('course_progress_id', None)
        if course_progress_id:
            course_progress = CourseProgress.objects.get(pk=course_progress_id)
            request.data['user_assessed_id'] = str(course_progress.user_id)
        request.data['user_who_assessed_id'] = str(request.user.id)

        response = super(AssessmentViewSet, self).create(request, *args, **kwargs)
        log_action(request)
        return response


