import django_filters
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from course_module_sections.models import CourseModuleSection, SectionVideoContainer, SectionText, SectionQuiz, \
    SectionAttachment, SectionImage, SectionGallery, SectionAssessment, SectionSurveyGroup
from course_module_sections.serializers import CourseModuleSectionSerializer, SectionVideoContainerSerializer, \
    SectionTextSerializer, SectionQuizSerializer, SectionAttachmentSerializer, SectionImageSerializer, \
    SectionGallerySerializer, SectionAssessmentSerializer, CourseModuleSectionFullSerializer, \
    SectionSurveyGroupSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from twz_server_django.utils import log_action


class CourseModuleSectionFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = CourseModuleSection
        fields = ['course_module_id', 'object_id', 'content_type']


class CourseModuleSectionViewSet(CreatedModifiedByModelViewSetMixin):
    """
    __list__:

    __update__:

    __partial_update__:

    __reorder__ [PUT]:

    A batch reorder method, simply send an array of objects with `{"id":"","order":""}`

    """
    queryset = CourseModuleSection.objects.filter()
    serializer_class = CourseModuleSectionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = CourseModuleSectionFilter
    full_serializer_class = CourseModuleSectionFullSerializer

    def list(self, request, *args, **kwargs):
        response = super(CourseModuleSectionViewSet, self).list(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])

            return super(CourseModuleSectionViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            obj = self.get_object()
            if 'order' in request.data:
                if request.data['order'] != obj.order:
                    obj.to(request.data['order'])

            return super(CourseModuleSectionViewSet, self).partial_update(request, *args, **kwargs)

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
            return super(CourseModuleSectionViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(CourseModuleSectionViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionVideoContainerFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionVideoContainer
        fields = ['vimeo_id',]


class SectionVideoContainerViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionVideoContainer.objects.filter()
    serializer_class = SectionVideoContainerSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionVideoContainerFilter
    search_fields = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionVideoContainerViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionVideoContainerViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionVideoContainerViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionTextFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionText
        fields = []


class SectionTextViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionText.objects.filter()
    serializer_class = SectionTextSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionTextFilter
    search_fields = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionTextViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            log_action(request)
            return super(SectionTextViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionTextViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionQuizFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionQuiz
        fields = ['quiz_id',]


class SectionQuizViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionQuiz.objects.filter()
    serializer_class = SectionQuizSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionQuizFilter
    search_fields = ('title',)

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionQuizViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionQuizViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionQuizViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionAttachmentFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionAttachment
        fields = []


class SectionAttachmentViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionAttachment.objects.filter()
    serializer_class = SectionAttachmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionAttachmentFilter
    search_filter = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAttachmentViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAttachmentViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAttachmentViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionImageFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionImage
        fields = []


class SectionImageViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionImage.objects.filter()
    serializer_class = SectionImageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionImageFilter
    search_fields = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionImageViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            log_action(request)
            return super(SectionImageViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionImageViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionGalleryFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionGallery
        fields = ['gallery_id',]


class SectionGalleryViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionGallery.objects.filter()
    serializer_class = SectionGallerySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionGalleryFilter
    search_filter = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionGalleryViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionGalleryViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionGalleryViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionAssessmentFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionAssessment
        fields = []


class SectionAssessmentViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionAssessment.objects.filter()
    serializer_class = SectionAssessmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    filter_class = SectionAssessmentFilter
    search_filter = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAssessmentViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAssessmentViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionAssessmentViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionSurveyGroupFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SectionSurveyGroup
        fields = ['survey', 'survey_group_id']


class SectionSurveyGroupViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SectionSurveyGroup.objects.filter()
    serializer_class = SectionSurveyGroupSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)
    search_filter = ('text', )

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionSurveyGroupViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionSurveyGroupViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(SectionSurveyGroupViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class SectionTypesViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CourseModuleSection.objects.all()

    def list(self, requst, *args, **kwargs):

        return Response([
            {
                "type": "section video container",
                "id": 19
            },
            {
                "type": "section assessment",
                "id": 20
            },
            {
                "type": "section quiz",
                "id": 21
            },
            {
                "type": "section image",
                "id": 22
            },
            {
                "type": "section attachment",
                "id": 23
            },
            {
                "type": "section text",
                "id": 24
            },
            {
                "type": "section gallery",
                "id": 46
            },
            {
                "type": "section survey group",
                "id": 55
            }
        ])
