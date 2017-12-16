import uuid
from uuid import UUID

import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import MethodNotAllowed, ParseError, NotFound
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from attachments.permissions import IsAllowedOrSuperuser
from course_module_sections.serializers import CourseModuleSectionSerializer, SectionVideoContainerSerializer, \
    SectionTextSerializer, SectionAttachmentSerializer, SectionImageSerializer, SectionAssessmentSerializer, \
    SectionQuizSerializer, SectionGallerySerializer, SectionSurveyGroupSerializer
from courses.models import Course, Category, CourseModule, CourseProgress
from courses.serializers import CourseSerializer, CourseCategorySerializer, CourseModuleSerializer, \
    CourseSerializerForPost, CourseProgressSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from twz_server_django.utils import log_action


class CourseFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Course
        fields = ['category', 'title', 'state', 'deleted', 'authors']


class CourseViewSet(CreatedModifiedByModelViewSetMixin):
    """
    __list__:

    __update__:

    __partial_update__:

    __reorder__ [PUT]:

    A batch reorder method, simply send an array of objects with `{"id":"","order":""}`

    """

    queryset = Course.objects.get_active()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ('title',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = CourseFilter

    def update(self, request, *args, **kwargs):
        self.serializer_class = CourseSerializerForPost
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])

            return super(CourseViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = CourseSerializerForPost
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])

            return super(CourseViewSet, self).partial_update(request, *args, **kwargs)

        raise MethodNotAllowed('PATCH')

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


    def create(self, request, *args, **kwargs):
        self.serializer_class = CourseSerializerForPost
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')

    def list(self, request, *args, **kwargs):
        self.queryset = Course.objects.get_with_is_started_queryset(user_id=request.user.id).order_by('is_started', 'category', '-rating')
        return super(CourseViewSet, self).list(request, *args, **kwargs)


class CourseCategoryFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Category
        fields = ['title', 'is_active', 'deleted']


class CourseCategoryViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Category.objects.get_active()
    serializer_class = CourseCategorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = CourseCategoryFilter
    search_fields = ('title','description')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseCategoryViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseCategoryViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseCategoryViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class CourseModuleFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = CourseModule
        fields = ['course', 'title', 'state', 'deleted']


class CourseModuleViewSet(CreatedModifiedByModelViewSetMixin):
    """
    __list__:

    __update__:

    __partial_update__:

    __reorder__ [PUT]:

    A batch reorder method, simply send an array of objects with `{"id":"","order":""}`

    """
    queryset = CourseModule.objects.get_active()
    serializer_class = CourseModuleSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ('title',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = CourseModuleFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        sections = instance.coursemodulesection_set.all()
        real_sections = []
        for section in sections:
            if section.related.__class__.__name__ == 'SectionVideoContainer':
                content = SectionVideoContainerSerializer(section.related).data
                content['type'] = 'video'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionText':
                content = SectionTextSerializer(section.related).data
                content['type'] = 'text'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionAttachment':
                content = SectionAttachmentSerializer(section.related).data
                content['type'] = 'attachment'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionImage':
                content = SectionImageSerializer(section.related).data
                content['type'] = 'image'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionAssessment':
                content = SectionAssessmentSerializer(section.related).data
                content['type'] = 'assessment'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionQuiz':
                content = SectionQuizSerializer(section.related).data
                content['type'] = 'quiz'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionGallery':
                content = SectionGallerySerializer(section.related).data
                content['type'] = 'gallery'
                content['section_id'] = section.id
                real_sections.append(content)
                continue
            if section.related.__class__.__name__ == 'SectionSurveyGroup':
                content = SectionSurveyGroupSerializer(section.related).data
                content['type'] = 'survey-group'
                content['section_id'] = section.id
                real_sections.append(content)
                continue

        serializer = self.get_serializer(instance)
        data = serializer.data

        data['sections'] = real_sections

        return Response(data)


    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])
            return super(CourseModuleViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])

            return super(CourseModuleViewSet, self).partial_update(request, *args, **kwargs)

        raise MethodNotAllowed('PATCH')

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

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            log_action(request)
            return super(CourseModuleViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseModuleViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class CourseProgressFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = CourseProgress
        fields = ['course_id', 'current_course_module_id', 'current_course_module_section_id', 'created_by_id', 'completed', 'ended']


class CourseProgressViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = CourseProgressFilter

    # def create(self, request, *args, **kwargs):
    #     log_action(request)
    #     return super(CourseProgressViewSet, self).create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        log_action(request)
        if 'course' not in request.data:
            raise ParseError({"detail": 'Course must be in the date body.'})
        try:
            current_progress = self.get_queryset().get(course=request.data['course'], created_by=request.user)
            current_progress.last_opened = timezone.datetime.now()
            current_progress.save()
            return Response(self.get_serializer(current_progress, many=False).data)
        except ObjectDoesNotExist:
            return super(CourseProgressViewSet, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser is False and request.user.is_staff is False:
            self.queryset = self.get_queryset().filter(created_by=request.user)

        log_action(request)
        if 'course' in request.GET:
            try:
                id = UUID(request.GET.get('course', None))
            except ValueError:
                raise ParseError({"detail": "The course should be a uuid."})

            try:
                current_progress = self.get_queryset().get(course=id, created_by=request.user)
            except ObjectDoesNotExist:
                raise NotFound({"detail": "Course is not started."})
            return Response(self.get_serializer(current_progress, many=False).data)
        else:
            return super(CourseProgressViewSet, self).list(request, *args, **kwargs)

            # return super(CourseProgressViewSet, self).list(request, *args, **kwargs)


