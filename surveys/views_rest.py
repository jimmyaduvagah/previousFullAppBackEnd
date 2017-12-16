import django_filters
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from attachments.permissions import IsAllowedOrSuperuser
from surveys.models import Survey, SurveyResponse
from surveys.serializers import SurveySerializer, SurveyResponseSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin


class SurveyViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    filter_backends = (OrderingFilter,)
    ordering_fields = ('created_on', 'title', 'created_by')

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyViewSet, self).list(request, *args, **kwargs)
        else:
            raise PermissionError()

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyViewSet, self).create(request, *args, **kwargs)
        else:
            raise PermissionError()

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyViewSet, self).destroy(request, *args, **kwargs)
        else:
            raise PermissionError()

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyViewSet, self).partial_update(request, *args, **kwargs)
        else:
            raise PermissionError()

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionError()




class SurveyResponseFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = SurveyResponse
        fields = ['survey', 'created_by', 'user', 'user']


class SurveyResponseViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = SurveyResponseFilter
    ordering_fields = ('created_on', 'user', 'survey')

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyResponseViewSet, self).list(request, *args, **kwargs)
        else:
            raise PermissionError()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        self.serializer = self.get_serializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)
        search = SurveyResponse.objects.filter(survey_id=self.serializer.data['survey'], user_id=request.user.id)
        if len(search) > 0:
            kwargs[self.lookup_field] = search[0].id
            self.kwargs[self.lookup_field] = search[0].id
            return super(SurveyResponseViewSet, self).update(request, *args, **kwargs)
        else:
            return super(SurveyResponseViewSet, self).create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyResponseViewSet, self).partial_update(request, *args, **kwargs)
        else:
            raise PermissionError()

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyResponseViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionError()

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser is True or request.user.is_staff:
            return super(SurveyResponseViewSet, self).destroy(request, *args, **kwargs)
        else:
            raise PermissionError()

